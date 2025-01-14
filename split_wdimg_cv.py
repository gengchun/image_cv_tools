import cv2

# 读取图像并转换为灰度图
img = cv2.imread('input.png')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# 二值化
_, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

# 形态学操作，增强块边界
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
dilated = cv2.dilate(binary, kernel, iterations=1)

# 轮廓检测
contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# 遍历轮廓并按大小过滤
blocks = []
for contour in contours:
    x, y, w, h = cv2.boundingRect(contour)
    if w > 50 and h > 50:  # 过滤小噪点
        block = img[y:y+h, x:x+w]
        blocks.append(block)

# 保存分割后的块
for idx, block in enumerate(blocks):
    cv2.imwrite(f'block_{idx}.png', block)
