import cv2
import numpy as np

def split_image_into_units(image_path):
    # 读取图像并预处理
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # 垂直投影分割列
    height, width = thresh.shape
    vertical_projection = np.sum(thresh, axis=0) // 255
    gap_threshold = 5  # 调整此参数以检测列间隙
    is_gap = vertical_projection < gap_threshold

    gap_starts, gap_ends = [], []
    in_gap = False
    for i in range(width):
        if is_gap[i]:
            if not in_gap:
                gap_starts.append(i)
                in_gap = True
        else:
            if in_gap:
                gap_ends.append(i-1)
                in_gap = False
    if in_gap:
        gap_ends.append(width-1)

    columns = []
    prev_end = 0
    for i in range(len(gap_starts)):
        if gap_starts[i] > prev_end:
            columns.append((prev_end, gap_starts[i]-1))
        prev_end = gap_ends[i] + 1
    if prev_end < width:
        columns.append((prev_end, width-1))

    # 处理每列进行水平分割
    all_units = []
    for x_start, x_end in columns:
        column_img = thresh[:, x_start:x_end+1]
        kernel = np.ones((5, 1), np.uint8)  # 合并文字行的间隙
        dilated = cv2.dilate(column_img, kernel, iterations=2)
        h_proj = np.sum(dilated, axis=1) // 255
        h_gap_threshold = 5  # 水平间隙阈值
        is_h_gap = h_proj < h_gap_threshold

        h_gap_starts, h_gap_ends = [], []
        in_h_gap = False
        for i in range(height):
            if is_h_gap[i]:
                if not in_h_gap:
                    h_gap_starts.append(i)
                    in_h_gap = True
            else:
                if in_h_gap:
                    h_gap_ends.append(i-1)
                    in_h_gap = False
        if in_h_gap:
            h_gap_ends.append(height-1)

        # 确定分割位置
        min_gap_height = 10  # 最小间隙高度
        split_positions = []
        for start, end in zip(h_gap_starts, h_gap_ends):
            if end - start + 1 >= min_gap_height:
                split_positions.append((start, end))

        # 生成单元坐标
        current_start = 0
        units = []
        for (s, e) in split_positions:
            split_line = (s + e) // 2
            if split_line > current_start:
                units.append((current_start, split_line))
            current_start = split_line + 1
        units.append((current_start, height-1))

        # 转换为全局坐标
        for y1, y2 in units:
            all_units.append((x_start, y1, x_end, y2))

    # 根据颜色判断单元类型并保存
    for idx, (x1, y1, x2, y2) in enumerate(all_units):
        unit_region = image[y1:y2+1, x1:x2+1]
        hsv = cv2.cvtColor(unit_region, cv2.COLOR_BGR2HSV)
        lower_black = np.array([0, 0, 0])
        upper_black = np.array([180, 255, 30])
        mask = cv2.inRange(hsv, lower_black, upper_black)
        black_ratio = np.sum(mask == 255) / (mask.size)
        if black_ratio > 0.5:
            type_str = 'ppt'
        else:
            type_str = 'text'
        cv2.imwrite(f'unit_{idx}_{type_str}.jpg', unit_region)

# 使用示例
split_image_into_units('input.jpg')