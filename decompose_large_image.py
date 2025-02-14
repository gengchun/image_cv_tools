import cv2
import numpy as np
import math

def process_large_image(input_path, output_folder, scale_ratio=0.2, min_ppt_area=50000):
    # 读取原始图像
    orig = cv2.imread(input_path)
    h, w = orig.shape[:2]
    
    # 生成缩放图像（保持宽高比）
    scaled_w = int(w * scale_ratio)
    scaled_h = int(h * scale_ratio)
    scaled_img = cv2.resize(orig, (scaled_w, scaled_h), interpolation=cv2.INTER_AREA)
    
    # 自适应灰度化和二值化
    gray = cv2.cvtColor(scaled_img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(gray, 255, 
                                  cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                  cv2.THRESH_BINARY_INV, 21, 4)
    
    # 形态学操作参数自动计算
    kernel_size = max(1, int(min(scaled_w, scaled_h)*0.005))
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    
    # 消除文字噪点
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel, iterations=1)
    
    # 轮廓检测
    contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # 筛选PPT区域
    ppt_contours = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > min_ppt_area * (scale_ratio**2):
            ppt_contours.append(cnt)
    
    # 创建缩放比例转换矩阵
    scale_matrix = np.array([[1/scale_ratio, 0], [0, 1/scale_ratio]])
    
    # 处理每个PPT区域
    for i, cnt in enumerate(ppt_contours):
        # 转换到原始坐标
        orig_cnt = np.round(cnt * scale_matrix).astype(np.int32)
        
        # 获取边界矩形
        x, y, cw, ch = cv2.boundingRect(orig_cnt)
        
        # 安全裁剪
        x1 = max(0, x)
        y1 = max(0, y)
        x2 = min(w, x + cw)
        y2 = min(h, y + ch)
        
        # 保存PPT区域
        cv2.imwrite(f"{output_folder}/ppt_{i}.png", orig[y1:y2, x1:x2])
        
        # 创建掩膜
        mask = np.zeros((h, w), dtype=np.uint8)
        cv2.drawContours(mask, [orig_cnt], -1, 255, -1)
        
        # 移除已处理的区域
        orig = cv2.inpaint(orig, mask, 3, cv2.INPAINT_TELEA)

    # 处理文字区域
    gray_orig = cv2.cvtColor(orig, cv2.COLOR_BGR2GRAY)
    text_thresh = cv2.adaptiveThreshold(gray_orig, 255, 
                                       cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY_INV, 31, 6)
    
    # 文本段落检测
    text_contours, _ = cv2.findContours(text_thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    
    # 文本区域处理
    text_index = 0
    for cnt in text_contours:
        area = cv2.contourArea(cnt)
        if 100 < area < 10000:
            x, y, w, h = cv2.boundingRect(cnt)
            # 扩展边界
            pad = 10
            x = max(0, x - pad)
            y = max(0, y - pad)
            w = min(orig.shape[1]-x, w + 2*pad)
            h = min(orig.shape[0]-y, h + 2*pad)
            
            # 保存文字区域
            cv2.imwrite(f"{output_folder}/text_{text_index}.png", orig[y:y+h, x:x+w])
            text_index += 1

if __name__ == "__main__":
    process_large_image("input.jpg", "output", scale_ratio=0.2, min_ppt_area=50000)