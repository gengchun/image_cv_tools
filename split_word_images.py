import cv2
import numpy as np

# 读取图像并转换为灰度图
img = cv2.imread('input.png')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# 二值化
_, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

# 计算水平投影直方图
h_projection = np.sum(binary == 0, axis=1)

# 找到分割点（空白行）
split_points = []
threshold = 5  # 空白行像素阈值
for i, val in enumerate(h_projection):
    if val <= threshold:
        split_points.append(i)

# 根据分割点提取块
blocks = []
start = 0
for i in range(1, len(split_points)):
    if split_points[i] - split_points[i-1] > 1:
        end = split_points[i]
        block = img[start:end, :]
        blocks.append(block)
        start = end

# 保存分割后的块
for idx, block in enumerate(blocks):
    cv2.imwrite(f'block_{idx}.png', block)
