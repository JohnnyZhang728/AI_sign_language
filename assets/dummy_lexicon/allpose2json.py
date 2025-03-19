import struct
import json
import os
import re
from pose_format import Pose

def read_string(file):
    """读取字符串（以长度为前缀）"""
    length = struct.unpack('H', file.read(2))[0]  # unsigned short for length
    return file.read(length).decode('utf-8')

def read_header(file):
    """解析 Header 部分"""
    version = struct.unpack('f', file.read(4))[0]  # float
    width, height, depth = struct.unpack('HHH', file.read(6))  # 3 unsigned shorts
    num_components = struct.unpack('H', file.read(2))[0]  # unsigned short
    # print("NUM_COMPONENTS:", num_components)

    components = []
    for _ in range(num_components):
        component_name = read_string(file)
        format_data = read_string(file)  # char[] Format
        num_points, num_limbs, num_colors = struct.unpack('HHH', file.read(6))

        points = [read_string(file) for _ in range(num_points)]
        limbs = [struct.unpack('HH', file.read(4)) for _ in range(num_limbs)]  # [From Point, To Point]
        colors = [struct.unpack('HHH', file.read(6)) for _ in range(num_colors)]  # [Red, Green, Blue]

        components.append({
            "name": component_name,
            "format": format_data,
            "points": points,
            "limbs": limbs,
            "colors": colors
        })

    return {
        "version": version,
        "width": width,
        "height": height,
        "depth": depth,
        "components": components
    }

def read_body(file, key_points):
    # print("key_points:", key_points)

    """解析 Body 部分"""
    fps, num_frames, num_people = struct.unpack('HHH', file.read(6))  # 3 unsigned shorts

    frames = []
    # print("key_points:", len(header['components']))

    # 先解析所有坐标 (X, Y, Z)
    for _ in range(num_frames):
        people = []
        for _ in range(num_people):
            person_components = []
            for _ in range(key_points):  # 按points
                x, y, z = struct.unpack('fff', file.read(12))  # 读取 float X, float Y, float Z
                person_components.append({"x": x, "y": y, "z": z})
            people.append(person_components)
        frames.append(people)

    # 再解析所有 confidence
    for frame_idx in range(num_frames):
        for person_idx in range(num_people):
            for comp_idx in range(key_points):
                confidence = struct.unpack('f', file.read(4))[0]  # 读取 float Confidence
                frames[frame_idx][person_idx][comp_idx]["confidence"] = confidence

    return {
        "fps": fps,
        "num_frames": num_frames,
        "num_people": num_people,
        "frames": frames
    }

def extract_number(filename):
    """从文件名中提取数字并返回整数（用于排序）"""
    match = re.search(r'(\d+)', filename)
    return int(match.group(1)) if match else float('inf')  # 如果没有数字，则放到最后

def process_pose_files(folder_path, output_json_path):
    """解析整个文件夹内的所有 .pose 文件，并存入一个 JSON"""
    all_poses = {}

    # 获取所有 .pose 文件，并按照数字大小排序
    pose_files = [f for f in os.listdir(folder_path) if f.endswith('.pose')]
    pose_files.sort(key=extract_number)  # 自然排序

    for pose_file in pose_files:
        file_path = os.path.join(folder_path, pose_file)

        with open(file_path, "rb") as file:
            data_buffer = file.read()
        # 使用 Pose 类解析文件
        pose = Pose.read(data_buffer)
        numpy_data = pose.body.data
        key_points = numpy_data.shape[2]

        with open(file_path, 'rb') as file:
            header = read_header(file)
            body = read_body(file, key_points)

        all_poses[pose_file] = {"header": header, "body": body}

    # 保存到 JSON 文件
    with open(output_json_path, "w") as json_file:
        json.dump(all_poses, json_file, indent=4)

    print(f"所有 .pose 文件已合并并保存到 {output_json_path}")

# 运行脚本
if __name__ == "__main__":
    folder_path = "/Users/zeyuzhang/TAMU/sign_language/sign_language_procesing/text_to_gloss_pose/spoken_to_signed/whisper_streaming/output_03_12/pose"
    output_json_path = "poses_for_poem_03_19.json"
    process_pose_files(folder_path, output_json_path)


