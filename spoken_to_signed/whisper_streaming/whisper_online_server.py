from whisper_online import *

import time
import argparse
import logging
import numpy as np

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from text_gloss import correct_ocr_text
from pose_gif import generate_pose, generate_gif, gpt_gloss, generate_video

import signal


lexicon_path = "/Users/zeyuzhang/TAMU/sign_language/sign_language_procesing/text_to_gloss_pose/assets/dummy_lexicon"
# output_pose_path = "output/pose/output_pose.pose"
# gif_path = "output/gif/output_gif.gif"
# video_path = "output/video/output_video.mp4"

# Usage: python whisper_online_server.py --lan en --backend openai-api
# python whisper_online_server.py --warmup-file samples_jfk.wav --lan en --backend openai-api
# Client(MacOS): ffmpeg -f avfoundation -i ":0" -ar 16000 -ac 1 -f s16le - | nc localhost 43007

logger = logging.getLogger(__name__)
parser = argparse.ArgumentParser()

# server options
parser.add_argument("--host", type=str, default='localhost')
parser.add_argument("--port", type=int, default=43007)
parser.add_argument("--warmup-file", type=str, dest="warmup_file", 
        help="The path to a speech audio wav file to warm up Whisper so that the very first chunk processing is fast. It can be e.g. https://github.com/ggerganov/whisper.cpp/raw/master/samples/jfk.wav .")

# options from whisper_online
add_shared_args(parser)
args = parser.parse_args()

set_logging(args,logger,other="")

# setting whisper object by args 

SAMPLING_RATE = 16000

size = args.model
language = args.lan
asr, online = asr_factory(args)
min_chunk = args.min_chunk_size

# warm up the ASR because the very first transcribe takes more time than the others. 
# Test results in https://github.com/ufal/whisper_streaming/pull/81
msg = "Whisper is not warmed up. The first chunk processing may take longer."
if args.warmup_file:
    if os.path.isfile(args.warmup_file):
        a = load_audio_chunk(args.warmup_file,0,1)
        asr.transcribe(a)
        logger.info("Whisper is warmed up.")
    else:
        logger.critical("The warm up file is not available. "+msg)
        sys.exit(1)
else:
    logger.warning(msg)


######### Server objects

import line_packet
import socket

class Connection:
    '''it wraps conn object'''
    PACKET_SIZE = 32000*5*60 # 5 minutes # was: 65536

    def __init__(self, conn):
        self.conn = conn
        self.last_line = ""

        self.conn.setblocking(True)

    def send(self, line):
        '''it doesn't send the same line twice, because it was problematic in online-text-flow-events'''
        if line == self.last_line:
            return
        line_packet.send_one_line(self.conn, line)
        self.last_line = line

    def receive_lines(self):
        in_line = line_packet.receive_lines(self.conn)
        return in_line

    def non_blocking_receive_audio(self):
        try:
            r = self.conn.recv(self.PACKET_SIZE)
            return r
        except ConnectionResetError:
            return None


import io
import soundfile

# wraps socket and ASR object, and serves one client connection. 
# next client should be served by a new instance of this object
class ServerProcessor:

    def __init__(self, c, online_asr_proc, min_chunk):
        self.connection = c
        self.online_asr_proc = online_asr_proc
        self.min_chunk = min_chunk

        self.last_end = None

        self.is_first = True

        self.counter = 0

        # 添加用于捕获 Ctrl+C 的信号处理器
        signal.signal(signal.SIGINT, self.handle_signal)

        self.start_time = None  # 保存开始时间
        self.end_time = None  # 保存结束时间

    def receive_audio_chunk(self):
        # receive all audio that is available by this time
        # blocks operation if less than self.min_chunk seconds is available
        # unblocks if connection is closed or a chunk is available

        # record audio start time
        start_time = time.time()
        print(f"\033[32mStart_time: {start_time} \033[0m")

        # processing audio receive
        out = []
        minlimit = self.min_chunk*SAMPLING_RATE
        while sum(len(x) for x in out) < minlimit:
            raw_bytes = self.connection.non_blocking_receive_audio()
            if not raw_bytes:
                break
#            print("received audio:",len(raw_bytes), "bytes", raw_bytes[:10])
            sf = soundfile.SoundFile(io.BytesIO(raw_bytes), channels=1,endian="LITTLE",samplerate=SAMPLING_RATE, subtype="PCM_16",format="RAW")
            audio, _ = librosa.load(sf,sr=SAMPLING_RATE,dtype=np.float32)
            out.append(audio)
        if not out:
            return None
        conc = np.concatenate(out)

        # record audio receive end time
        end_time = time.time()
        print(f"Audio received in {end_time - start_time:.3f} seconds.")

        if self.is_first and len(conc) < minlimit:
            return None
        self.is_first = False
        return np.concatenate(out)

    def format_output_transcript(self,o):
        # output format in stdout is like:
        # 0 1720 Takhle to je
        # - the first two words are:
        #    - beg and end timestamp of the text segment, as estimated by Whisper model. The timestamps are not accurate, but they're useful anyway
        # - the next words: segment transcript

        # This function differs from whisper_online.output_transcript in the following:
        # succeeding [beg,end] intervals are not overlapping because ELITR protocol (implemented in online-text-flow events) requires it.
        # Therefore, beg, is max of previous end and current beg outputed by Whisper.
        # Usually it differs negligibly, by appx 20 ms.

        # record WHISPER transcript time
        start_time = time.time()

        if o[0] is not None:
            beg, end = o[0]*1000,o[1]*1000
            if self.last_end is not None:
                beg = max(beg, self.last_end)

            self.last_end = end
            # print("%1.0f %1.0f %s" % (beg,end,o[2]),flush=True,file=sys.stderr)
            # return "%1.0f %1.0f %s" % (beg,end,o[2])

            # record WHISPER transcript end time
            end_time = time.time()
            print(f"Whisper transcription completed in {end_time - start_time:.3f} seconds.")

            return o[2]
        else:
            logger.debug("No text in this segment")
            return None

    def send_result(self, o):
        msg = self.format_output_transcript(o)
        if msg is not None:
            self.connection.send(msg)

            # 将结果追加到本地文件
            # with open("transcription_results.txt", "a", encoding="utf-8") as f:
            #     f.write(msg + "\n")

            # 也可以打印出来
            print("Real-time Transcript:", msg)

            # Text to Gloss
            gloss_start_time = time.time()  # 记录 Gloss 开始时间
            gloss = gpt_gloss(msg)
            gloss_end_time = time.time()  # 记录 Gloss 完成时间
            print("Real-time Gloss:", gloss)
            print(f"Gloss generation completed in {gloss_end_time - gloss_start_time:.3f} seconds.")

            # Gloss to Pose
            pose_start_time = time.time()  # 记录 Pose 开始时间
            # 使用累积计数值生成唯一文件名
            self.counter += 1  # 每次生成一个新的 pose 时，计数器加 1
            pose_filename = f"pose_{self.counter}.pose"  # 例如，pose_1.txt
            gif_filename = f"gif_{self.counter}.gif"  # 对应的 GIF 文件名
            video_filename = f"video_{self.counter}.mp4"

            # 文件夹路径
            output_dir = "output"
            pose_dir = f"{output_dir}/pose"
            gif_dir = f"{output_dir}/gif"
            video_dir = f"{output_dir}/video"

            # 如果这些文件夹不存在，则先创建它们
            os.makedirs(pose_dir, exist_ok=True)
            os.makedirs(gif_dir, exist_ok=True)
            os.makedirs(video_dir, exist_ok=True)

            output_pose_path = f"{pose_dir}/{pose_filename}"
            gif_path = f"{gif_dir}/{gif_filename}"
            video_path = f"{video_dir}/{video_filename}"

            # output_pose_path = f"output/pose/{pose_filename}"
            # gif_path = f"output/gif/{gif_filename}"
            # video_path = f"output/video/{video_filename}"

            # generate_pose(gloss, lexicon_path, output_pose_path)
            # generate_gif(output_pose_path, gif_path)

            try:
                # 尝试执行 generate_pose，捕获潜在的异常
                generate_pose(gloss, lexicon_path, output_pose_path)
                # generate_gif(output_pose_path, gif_path)
                # generate_video(output_pose_path, video_path)
                pose_end_time = time.time()  # 记录 Pose 完成时间
                print(f"Pose generation completed in {pose_end_time - pose_start_time:.3f} seconds.")

            except Exception as e:
                # 捕获异常并打印警告，跳过当前 msg 的处理
                print(f"Warning: {e}, skipping this message...")
                # 跳过当前 msg，继续下一个
                return

    def handle_signal(self, signum, frame):
        # 捕获到 Ctrl+C 时调用
        if self.start_time:
            self.end_time = time.time()
            print(f"\033[32mEnd_time: {self.end_time} \033[0m")
            print(f"\033[32mTotal processing time for this chunk: {self.end_time - self.start_time:.3f} seconds\033[0m")
        else:
            print("\033[32mProgram interrupted before processing started.\033[0m")
        sys.exit(0)  # 确保程序退出


    def process(self):
        # handle one client connection
        # 记录整个流程的开始时间
        start_time = time.time()
        self.start_time = time.time()  # 记录开始时间

        self.online_asr_proc.init()
        while True:
            a = self.receive_audio_chunk()
            if a is None:
                break
            self.online_asr_proc.insert_audio_chunk(a)
            o = online.process_iter()
            try:
                self.send_result(o)
            except BrokenPipeError:
                logger.info("broken pipe -- connection closed?")
                break

        # 记录整个处理过程的结束时间
        end_time = time.time()
        print(f"Total processing time for this chunk: {end_time - start_time:.3f} seconds")

        # 如果 Ctrl+C 没有被捕获，总延迟时间会在这里打印
        if self.end_time is None:  # 如果没有被中断，则正常打印
            self.end_time = time.time()
            print(f"\033[32mTotal processing time for this chunk: {self.end_time - self.start_time:.3f} seconds\033[0m")

#        o = online.finish()  # this should be working
#        self.send_result(o)



# server loop

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((args.host, args.port))
    s.listen(1)
    logger.info('Listening on'+str((args.host, args.port)))
    while True:
        conn, addr = s.accept()
        logger.info('Connected to client on {}'.format(addr))
        connection = Connection(conn)
        proc = ServerProcessor(connection, online, args.min_chunk_size)
        proc.process()
        conn.close()
        logger.info('Connection to client closed')
logger.info('Connection closed, terminating.')
