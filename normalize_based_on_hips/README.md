## Setup

Find the `pose_format` Python library in your Python Env. 

e.g. `/Users/username/opt/anaconda3/envs/py39/lib/python3.9/site-packages/pose_format/`

Replace `pose_format/pose.py`, `pose_format/utils/holistic.py`, `pose_format/utils/generic.py`. 

In `holistic.py`, we updated the pose coordinates (x, y) range.

Previous (for display in video/gif):

X: [-1, 1] → * width → [-width, width]  
Y: [-1, 1] → * height → [-height, height]

Present:

X: [-1, 1]  
Y: [-1, 1]

In `generic.py`,  we added a new function `pose_hips()`  replace the older `pose_shoulders()`.

In `pose.py`, we modified the `normalize()` function to perform normalization only on the `x` and `y` coordinates, while leaving `z` unchanged.

In `concatenat.py` in the project files, we removed the previous scaling method which is used for displaying in 2D videos.

## Generate poses dataset for lexicon

```
videos_to_poses --format mediapipe --directory /path/to/videos
```

videos_dataset download [link](https://drive.google.com/file/d/1N1z45HK2XsEs1KFVPjoaPb2jDPhxCx55/view?usp=sharing).





