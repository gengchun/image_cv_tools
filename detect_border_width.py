import cv2
import numpy as np

def detect_border_width(img_path, color_diff_threshold=50, sample_lines=10):
    img = cv2.imread(img_path)
    if img is None:
        raise ValueError("Image not found")
    
    h, w = img.shape[:2]
    results = {'top':0, 'bottom':0, 'left':0, 'right':0}

    def find_edge(roi, axis):
        grad = np.abs(np.diff(roi, axis=axis))
        grad_mean = np.mean(grad, axis=(not axis, 2))
        threshold = np.max(grad_mean) * 0.8
        edges = np.where(grad_mean > threshold)[0]
        return edges[0] if len(edges) > 0 else 0

    # 上端の幅検出
    sample_step = h // sample_lines
    top_edges = []
    for y in range(0, h, sample_step):
        roi = img[y:y+1, :, :]
        edge = find_edge(roi, axis=0)
        top_edges.append(edge)
    results['top'] = int(np.median(top_edges))

    # 下端の幅検出
    bottom_edges = []
    for y in range(h-1, 0, -sample_step):
        roi = img[y:y+1, :, :]
        edge = find_edge(roi, axis=0)
        bottom_edges.append(edge)
    results['bottom'] = int(np.median(bottom_edges))

    # 左端の幅検出
    sample_step = w // sample_lines
    left_edges = []
    for x in range(0, w, sample_step):
        roi = img[:, x:x+1, :]
        edge = find_edge(roi, axis=1)
        left_edges.append(edge)
    results['left'] = int(np.median(left_edges))

    # 右端の幅検出
    right_edges = []
    for x in range(w-1, 0, -sample_step):
        roi = img[:, x:x+1, :]
        edge = find_edge(roi, axis=1)
        right_edges.append(edge)
    results['right'] = int(np.median(right_edges))

    return results