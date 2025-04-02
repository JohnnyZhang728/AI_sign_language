import struct
import json
import numpy as np
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
    # print("num_components", num_components)

    components = []
    for _ in range(num_components):
        component_name = read_string(file)
        format_data = read_string(file)  # char[] Format
        num_points, num_limbs, num_colors = struct.unpack('HHH', file.read(6))
        # print("num_points", num_points)

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

def pose_to_json(file_path):
    with open(file_path, "rb") as file:
        data_buffer = file.read()

    # 使用 Pose 类解析文件
    pose = Pose.read(data_buffer)
    numpy_data = pose.body.data
    key_points = numpy_data.shape[2]

    with open(file_path, 'rb') as file:
        # Step 1: 解析 Header
        header = read_header(file)
        # print("Header:", header)

        # Step 2: 解析 Body
        body = read_body(file, key_points)
        # print("Body:", body)

    # with open(output_json, "w") as json_file:
    #     json.dump({"header": header, "body": body}, json_file, indent=4)

    return json.dumps({"header": header, "body": body})



# 主函数
if __name__ == "__main__":
    file_path = "output/pose/pose_3.pose"


    with open(file_path, "rb") as file:
        data_buffer = file.read()

    # 使用 Pose 类解析文件
    pose = Pose.read(data_buffer)
    numpy_data = pose.body.data
    key_points = numpy_data.shape[2]

    with open(file_path, 'rb') as file:
        # Step 1: 解析 Header
        header = read_header(file)
        print("Header:", header)

        # Step 2: 解析 Body
        body = read_body(file, key_points)
        print("Body:", body)

    # output_json = "/Users/zeyuzhang/TAMU/sign_language/sign_language_procesing/text_to_gloss_pose/spoken_to_signed/video_to_pose/test/COCAINE_5.json"
    output_json = "output/pose/pose_3.json"
    with open(output_json, "w") as json_file:
        json.dump({"header": header, "body": body}, json_file, indent=4)


