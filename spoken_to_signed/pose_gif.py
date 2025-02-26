import os
import sys
import subprocess
from pose_format import Pose
from pose_format.pose_visualizer import PoseVisualizer
from rich import print
from PIL import Image
from text_gloss import correct_ocr_text
import cv2

def generate_pose(text, lexicon_path, output_pose_path):
    # Generate .pose file using text_to_gloss_to_pose command
    command = [
        "text_to_gloss_to_pose",
        "--text", text,
        "--glosser", "simple",
        "--lexicon", lexicon_path,
        "--spoken-language", "en",
        "--signed-language", "sgg",
        "--pose", output_pose_path
    ]
    subprocess.run(command, check=True)

def generate_gif(pose_file_path, gif_path):
    # Open and read the pose file
    with open(pose_file_path, "rb") as f:
        p = Pose.read(f.read())

    # Resize to 256, for visualization speed
    scale = p.header.dimensions.width / 256
    p.header.dimensions.width = int(p.header.dimensions.width / scale)
    p.header.dimensions.height = int(p.header.dimensions.height / scale)
    p.body.data = p.body.data / scale

    # Generate .gif
    v = PoseVisualizer(p)
    v.save_gif(gif_path, v.draw())

    # # Open and display the generated GIF
    # gif_image = Image.open(gif_path)
    # gif_image.show()

    # Optionally print a confirmation message
    print("[bold green]GIF generated successfully![/bold green]")

def split_fs_words(input_str):
    """
    Splits all words that start with 'fs-' into individual letters in a given string.

    Args:
        input_str (str): The input string.

    Returns:
        str: The modified string with 'fs-' words split into individual letters.
    """
    words = input_str.split()
    result = []

    for word in words:
        if word.startswith("fs-"):
            # Remove 'fs-' and split the remaining part into letters
            letters = " ".join(word[3:])
            result.append(letters)
        else:
            # 如果没有 'fs-'，去掉单词中的连词符号并拆分为单独的单词
            word_parts = word.replace("-", " ").split()
            result.extend(word_parts)
            # result.append(word)

    return " ".join(result)

def read_text_from_file(file_path):

    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def gpt_gloss(text):
    corrected_text = correct_ocr_text(text)
    corrected_fs_text = split_fs_words(corrected_text)
    return corrected_fs_text


def generate_video(pose_file_path, video_path):
    # Open and read the pose file
    with open(pose_file_path, "rb") as f:
        p = Pose.read(f.read())

    # Resize to 256, for visualization speed
    scale = p.header.dimensions.width / 256
    p.header.dimensions.width = int(p.header.dimensions.width / scale)
    p.header.dimensions.height = int(p.header.dimensions.height / scale)
    p.body.data = p.body.data / scale

    # Generate .gif
    v = PoseVisualizer(p)
    v.save_video(video_path, v.draw())

    # Optionally print a confirmation message
    print("[bold green]VIDEO generated successfully![/bold green]")


# def generate_video(pose_file_path, video_path, fps=30):
#     # Open and read the pose file
#     with open(pose_file_path, "rb") as f:
#         p = Pose.read(f.read())
#
#     # Resize to 256, for visualization speed
#     scale = p.header.dimensions.width / 256
#     p.header.dimensions.width = int(p.header.dimensions.width / scale)
#     p.header.dimensions.height = int(p.header.dimensions.height / scale)
#     p.body.data = p.body.data / scale
#
#     # Generate frames
#     v = PoseVisualizer(p)
#     frames = list(v.draw())  # 获取所有帧 (List[np.ndarray])
#
#     # 获取视频宽高
#     height, width, _ = frames[0].shape
#     fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # 使用MP4编码
#     video_writer = cv2.VideoWriter(video_path, fourcc, fps, (width, height))
#
#     # 写入帧到视频
#     for frame in frames:
#         # video_writer.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))  # OpenCV使用BGR格式
#         video_writer.write(frame)
#
#     # 释放资源
#     video_writer.release()
#     print("[bold green]Video generated successfully![/bold green]")



def main():
    # Set the input text here
    # text_input = "I want a cat."
    text_input = "My name is DAVID."
    # text_input = "../input_poems/New_Orleans_Function_by_Michael_Collins.txt"
    # text_input = read_text_from_file(text_input)

    lexicon_path = "/Users/zeyuzhang/TAMU/sign_language/sign_language_procesing/text_to_gloss_pose/assets/dummy_lexicon"
    output_pose_path = "../assets/dummy_lexicon/output/pose/output_pose.pose"
    gif_path = "../assets/dummy_lexicon/output/gif/output_gif.gif"
    video_path = "../assets/dummy_lexicon/output/video/output_video.mp4"

    # Correct the OCR text
    corrected_text = correct_ocr_text(text_input)
    print("text to gloss using chatgpt:", corrected_text)

    corrected_text = split_fs_words(corrected_text)


    # print(corrected_text)

    # Generate pose and GIF
    generate_pose(corrected_text, lexicon_path, output_pose_path)
    generate_gif(output_pose_path, gif_path)
    generate_video(output_pose_path, video_path)

if __name__ == "__main__":
    main()

