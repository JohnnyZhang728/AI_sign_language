import os
import json
import shutil

# define file path
json_path = '/Users/wenyaogao/PycharmProjects/spoken-to-signed-translation/assets/dummy_lexicon/selected_video/selected.json'
video_source_path = '/Users/wenyaogao/Downloads/archive/videos'
target_directory = '/Users/wenyaogao/PycharmProjects/spoken-to-signed-translation/assets/dummy_lexicon/selected_video/video_english'

# create path (if not exist)
os.makedirs(target_directory, exist_ok=True)

# read selected.json
with open(json_path, 'r', encoding='utf-8') as file:
    selected_dict = json.load(file)

# iterate selected.json
for english_word, video_id in selected_dict.items():
    # read video_id vido and target video path
    video_file_name = f'{video_id}.mp4'
    source_video_path = os.path.join(video_source_path, video_file_name)

    # create
    target_video_name = f'{english_word}.mp4'
    target_video_path = os.path.join(target_directory, target_video_name)

    # check if original file exist
    if os.path.exists(source_video_path):
        # copy and rename the file
        shutil.copy2(source_video_path, target_video_path)
        print(f'Successfully copied {source_video_path} to {target_video_path}')
    else:
        print(f'Video file {source_video_path} not found!')

print('All videos processed.')
