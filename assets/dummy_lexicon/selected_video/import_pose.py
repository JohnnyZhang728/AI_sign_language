import os
import shutil

source_directory = '/Users/wenyaogao/Desktop/123/pose'  # pue your converted pose file path here
pose_directory = '../sgg'  # save to pose directory
mp4_directory = '/Users/wenyaogao/Desktop/123/video'  # directory path where you save your mp4 video

# check directory
os.makedirs(pose_directory, exist_ok=True)
os.makedirs(mp4_directory, exist_ok=True)

# iterate through all file in target directory
for filename in os.listdir(source_directory):
    source_file_path = os.path.join(source_directory, filename)

    # determine if this is file
    if os.path.isfile(source_file_path):
        if filename.endswith('.pose'):
            # construct target .pose file path
            target_file_path = os.path.join(pose_directory, filename)
            # move .pose file
            shutil.move(source_file_path, target_file_path)
            print(f'Moved {source_file_path} to {target_file_path}')
        elif filename.endswith('.mp4'):
            # construct .mp4 file target path
            target_file_path = os.path.join(mp4_directory, filename)
            # move .mp4 files
            shutil.move(source_file_path, target_file_path)
            print(f'Moved {source_file_path} to {target_file_path}')

print('All files have been processed.')
