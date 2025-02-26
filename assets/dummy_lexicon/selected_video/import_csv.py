import os
import csv

# 定义文件路径
source_directory = '../sgg/'  # directory save .pose files
csv_file_path = '../index.csv' # CSV file path

# 读取现有的CSV文件内容
csv_rows = []
if os.path.exists(csv_file_path):
    with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        csv_rows = list(reader)

# Add new .pose file info to csv_rows
for filename in os.listdir(source_directory):
    if filename.endswith('.pose'):
        # 获取单词和gloss
        word = filename[:-5]  # delete file suffix .pose
        gloss = word.upper()

        # construct new row in csv
        new_row = [
            f'sgg/{filename}',  # path
            'en',               # spoken_language
            'sgg',              # signed_language
            '0',                # start
            '0',                # end
            word,               # words
            gloss,              # glosses
            '0'                 # priority
        ]
        csv_rows.append(new_row)

# update with new content
with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(csv_rows)

print('All .pose files have been imported into the CSV file.')
