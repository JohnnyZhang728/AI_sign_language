import json


def parse_pose_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.read().split('\n')

    data = []
    block = {}

    for line in lines:
        line = line.strip()
        if not line:
            if block:
                data.append(block)
                block = {}
            continue
        if line.endswith('.pose'):
            block['pose_name'] = line.replace('.pose', '')
        elif line.startswith('start_time:'):
            block['start_time'] = line.split('start_time:')[1].strip()
        elif line.startswith('Real-time_Transcript:'):
            block['transcript'] = line.split('Real-time_Transcript:')[1].strip()
        elif line.startswith('Real-time_Gloss:'):
            block['gloss'] = line.split('Real-time_Gloss:')[1].strip()

    if block:  # Add the last block if not added
        data.append(block)

    return data


# 使用示例
pose_data = parse_pose_file('0501/Afterlight/clean_output.txt')

with open('0501/Afterlight/timestamp_json/timestamp.json', 'w', encoding='utf-8') as out_file:
    json.dump(pose_data, out_file, indent=2, ensure_ascii=False)

print("✅ JSON 文件已生成：output.json")
