from pose_format import Pose

# 打开并读取 .pose 文件
file_path = "asl/name.pose"
with open(file_path, "rb") as file:
    data_buffer = file.read()

# 使用 Pose 类解析文件
pose = Pose.read(data_buffer)

# 读取 Header 中的 depth 和 Format
depth = pose.header.dimensions.depth
# print(pose.body.data)
formats = [component.format for component in pose.header.components]
limbs = [component.limbs for component in pose.header.components]
print("limbs:", limbs)
points = [component.points for component in pose.header.components]
print("points:", points)
names = [component.name for component in pose.header.components]
print("names:", names)
colors = [component.colors for component in pose.header.components]
print("colors:", colors)


# 打印结果
print("Depth:", depth)
print("Formats:", formats)

# print("confidence:", pose.body.confidence)

import numpy as np

numpy_data = pose.body.data
confidence = pose.body.confidence

print("Data Shape:", numpy_data.shape)  # 输出数据的形状
print("Confidence Shape:", confidence.shape)  # 输出置信度的形状

"""
    pose.body.data

    
    data: 
        Data in the format (Frames, People, Points, Dims) e.g., (74, 1, 178, 3).
    confidence: 
        Confidence data in the format (Frames, People, Points) e.g., (74, 1, 178).


"""





import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# 获取第一帧第一个人的数据
first_frame = numpy_data[36, 0]  # Shape: (178, 3), 178个点，每点有3个维度(X, Y, Z)
x, y, z = first_frame[:, 0], first_frame[:, 1], first_frame[:, 2]

# 创建3D可视化
fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111, projection='3d')
ax.scatter(x, y, z, c='b', marker='o')  # 蓝色点，形状为圆圈
ax.set_title("3D Pose Visualization (Frame 36, Person 0)")
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
plt.show()


