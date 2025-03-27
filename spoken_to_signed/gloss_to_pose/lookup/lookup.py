import os
from collections import defaultdict
from typing import List

from pose_format import Pose

from spoken_to_signed.text_to_gloss.types import Gloss

import numpy as np


class PoseLookup:
    def __init__(self, rows: List, directory: str = None):
        self.directory = directory

        self.words_index = self.make_dictionary_index(rows, based_on="words")
        self.glosses_index = self.make_dictionary_index(rows, based_on="glosses")

        self.file_systems = {}

    def make_dictionary_index(self, rows: List, based_on: str):
        # As an attempt to make the index more compact in memory, we store a dictionary with only what we need
        languages_dict = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        for d in rows:
            lower_term = d[based_on].lower()
            languages_dict[d['spoken_language']][d['signed_language']][lower_term].append({
                "path": d['path'],
                "start": d['start'],
                "end": d['end'],
            })
        return languages_dict

    def read_pose(self, pose_path: str):
        if pose_path.startswith('gs://'):
            if 'gcs' not in self.file_systems:
                import gcsfs
                self.file_systems['gcs'] = gcsfs.GCSFileSystem(anon=True)

            with self.file_systems['gcs'].open(pose_path, "rb") as f:
                return Pose.read(f.read())

        if pose_path.startswith('https://'):
            raise NotImplementedError("Can't access pose files from https endpoint")

        if self.directory is None:
            raise ValueError("Can't access pose files without specifying a directory")

        pose_path = os.path.join(self.directory, pose_path)
        with open(pose_path, "rb") as f:
            return Pose.read(f.read())

    def lookup(self, word: str, gloss: str, spoken_language: str, signed_language: str, source: str = None) -> Pose:
        lookup_list = [
            (self.words_index, (spoken_language, signed_language, word)),
            (self.glosses_index, (spoken_language, signed_language, word)),
            (self.glosses_index, (spoken_language, signed_language, gloss)),
        ]

        for dict_index, (spoken_language, signed_language, term) in lookup_list:
            if spoken_language in dict_index:
                if signed_language in dict_index[spoken_language]:
                    lower_term = term.lower()
                    if lower_term in dict_index[spoken_language][signed_language]:
                        rows = dict_index[spoken_language][signed_language][lower_term]
                        # TODO maybe perform additional string match, for correct casing
                        return self.read_pose(rows[0]["path"])

        raise FileNotFoundError

    '''
    def lookup_sequence(self, glosses: Gloss, spoken_language: str, signed_language: str, source: str = None):
        poses: List[Pose] = []
        # print(glosses)
        for word, gloss in glosses:
            try:
                pose = self.lookup(word, gloss, spoken_language, signed_language)
                poses.append(pose)
            except FileNotFoundError:
                # word_gloss = f"{word}/{gloss}"
                # print(f"No pose found for {word_gloss}")
                print(f"No pose found for {word}/{gloss}")
                pass

        if len(poses) == 0:
            gloss_sequence = ' '.join([f"{word}/{gloss}" for word, gloss in glosses])
            print(f"Warning: No poses found for {gloss_sequence}, skipping...")
            # raise Exception(f"No poses found for {gloss_sequence}")

        return poses
    '''

    def lookup_sequence(self, glosses: Gloss, spoken_language: str, signed_language: str, source: str = None):
        poses: List[Pose] = []
        # print(glosses)
        for i, (word, gloss) in enumerate(glosses):
            # print("word:", word)
            # print("gloss:", gloss)

            try:
                pose = self.lookup(word, gloss, spoken_language, signed_language)
                poses.append(pose)
            except FileNotFoundError:
                # word_gloss = f"{word}/{gloss}"
                # print(f"No pose found for {word_gloss}")
                print(f"No pose found for {word}/{gloss}")
                pass

            # 如果当前 gloss 是 '?'，则对前一个 pose 进行眉毛调整
            if gloss == '?' and i > 0:
                if len(poses) > 0:
                    poses[-1] = raise_eyebrows(poses[-1])


        if len(poses) == 0:
            gloss_sequence = ' '.join([f"{word}/{gloss}" for word, gloss in glosses])
            print(f"Warning: No poses found for {gloss_sequence}, skipping...")
            # raise Exception(f"No poses found for {gloss_sequence}")

        return poses

def raise_eyebrows(pose: Pose, raise_amount=5) -> Pose:

    frames, people, points, dims = pose.body.data.shape
    person_idx = 0

    raise_frames = int(frames * 0.6)  # eyebrows raising frames
    pad_frames = int(frames * 0.13)  # waiting frames before raise eyebrows

    rise_phase = int(raise_frames * 0.1)
    hold_phase = int(raise_frames * 0.8)
    fall_phase = int(raise_frames * 0.1)

    LEFT_BROW_POINTS = []
    RIGHT_BROW_POINTS = []

    if points == 178:
        print("raising eyebrows for '?'")

        LEFT_BROW_POINTS = [19, 20, 21, 23, 26, 27, 28, 30, 42, 43]
        RIGHT_BROW_POINTS = [81, 82, 83, 85, 88, 89, 90, 92, 104, 105]

    elif points == 576:
        print("raising eyebrows for '?'")

        LEFT_BROW_POINTS = [79, 85, 86, 88, 96, 98, 99, 103, 138, 140]
        RIGHT_BROW_POINTS = [309, 315, 316, 318, 326, 328, 329, 333, 367, 369]

    for i in range(raise_frames):
        if i < rise_phase:
            factor = np.sin((i / rise_phase) * (np.pi / 2))
        elif i < rise_phase + hold_phase:
            factor = 1
        else:
            factor = np.cos(((i - rise_phase - hold_phase) / fall_phase) * (np.pi / 2))

        for p in LEFT_BROW_POINTS + RIGHT_BROW_POINTS:
            pose.body.data[pad_frames + i, person_idx, p, 1] -= factor * raise_amount

    return pose


