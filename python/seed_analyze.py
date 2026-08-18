#!/home/a-pages/python/venv/bin/python
# Python 3.6 / NumPy 1.19.5 / OpenCV 4.5.5 compatible
import argparse, json, math, os, platform, sys, time
import cv2
import numpy as np

ALGORITHM_VERSION = '2.2.1-illumination-adaptive-local-watershed'

def emit(data):
    sys.stdout.write(json.dumps(data, ensure_ascii=False, separators=(',', ':')))
    sys.stdout.flush()

def odd(value):
    value = max(1, int(value))
    return value if value % 2 else value + 1

def safe_mean(values):
    return float(np.mean(values)) if values else 0.0

def safe_std(values):
    return float(np.std(values)) if values else 0.0

def stats(values):
    mean = safe_mean(values)
    std = safe_std(values)
    return {
        'mean': round(mean, 4),
        'std': round(std, 4),
        'min': round(float(min(values)), 4) if values else 0.0,
        'max': round(float(max(values)), 4) if values else 0.0,
        'cv_percent': round((std / mean * 100.0), 3) if mean > 0 else 0.0,
    }

def save_stage(stage_dir, name, image):
    if not stage_dir:
        return None
    if not os.path.isdir(stage_dir):
        os.makedirs(stage_dir)
    path = os.path.join(stage_dir, name + '.jpg')
    cv2.imwrite(path, image, [int(cv2.IMWRITE_JPEG_QUALITY), 88])
    return path

def contours_from_watershed(image, binary, distance_ratio, bg_iterations, peak_kernel):
    kernel = np.ones((3, 3), np.uint8)
    sure_bg = cv2.dilate(binary, kernel, iterations=max(1, int(bg_iterations)))
    distance = cv2.distanceTransform(binary, cv2.DIST_L2, 5)
    max_distance = float(distance.max())
    # Build markers per connected foreground component. This prevents the
    # largest seed from setting a global threshold that erases smaller seeds.
    _, components = cv2.connectedComponents(binary)
    markers = np.zeros(binary.shape, dtype=np.int32)
    marker_id = 1
    pk = odd(max(3, int(peak_kernel)))
    peak_element = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (pk, pk))
    for component_id in range(1, int(components.max()) + 1):
        component_mask = components == component_id
        values = np.where(component_mask, distance, 0)
        component_max = float(values.max())
        if component_max <= 0:
            continue
        smoothed = cv2.GaussianBlur(values.astype(np.float32), (0, 0), max(1.0, pk / 8.0))
        dilated = cv2.dilate(smoothed, peak_element)
        peaks = component_mask & (smoothed >= dilated - 1e-4) & (smoothed >= component_max * max(0.05, min(0.95, float(distance_ratio))))
        peak_u8 = np.uint8(peaks) * 255
        peak_u8 = cv2.dilate(peak_u8, np.ones((3, 3), np.uint8), iterations=1)
        peak_count, peak_labels = cv2.connectedComponents(peak_u8)
        if peak_count <= 1:
            # Safe fallback: keep the component as one seed marker.
            core = np.uint8(component_mask & (distance >= component_max * max(0.25, float(distance_ratio)))) * 255
            _, peak_labels = cv2.connectedComponents(core)
            peak_count = int(peak_labels.max()) + 1
        for local_id in range(1, peak_count):
            markers[peak_labels == local_id] = marker_id
            marker_id += 1
    sure_fg = np.uint8(markers > 0) * 255
    unknown = cv2.subtract(sure_bg, sure_fg)
    markers = markers + 1
    markers[unknown == 255] = 0
    markers = cv2.watershed(image.copy(), markers)
    contours = []
    for label in range(2, int(markers.max()) + 1):
        mask = np.zeros(binary.shape, dtype=np.uint8)
        mask[markers == label] = 255
        found = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cs = found[0] if len(found) == 2 else found[1]
        if cs:
            contours.append(max(cs, key=cv2.contourArea))
    distance_view = np.uint8(np.clip(distance / max_distance * 255.0, 0, 255)) if max_distance > 0 else distance
    marker_view = np.zeros_like(image)
    marker_view[markers == -1] = (0, 0, 255)
    marker_view[markers > 1] = (0, 180, 0)
    return contours, distance_view, marker_view, marker_id - 1

def object_metrics(contour, scale_px_per_mm):
    area = float(cv2.contourArea(contour))
    perimeter = float(cv2.arcLength(contour, True))
    x, y, w, h = cv2.boundingRect(contour)
    hull_area = float(cv2.contourArea(cv2.convexHull(contour)))
    solidity = area / hull_area if hull_area > 0 else 0.0
    extent = area / float(w * h) if w > 0 and h > 0 else 0.0
    circularity = 4.0 * math.pi * area / (perimeter * perimeter) if perimeter > 0 else 0.0
    moments = cv2.moments(contour)
    cx = float(moments['m10'] / moments['m00']) if moments['m00'] else float(x + w / 2.0)
    cy = float(moments['m01'] / moments['m00']) if moments['m00'] else float(y + h / 2.0)
    if len(contour) >= 5:
        (_, _), (axis_a, axis_b), angle = cv2.fitEllipse(contour)
        major = float(max(axis_a, axis_b))
        minor = float(min(axis_a, axis_b))
        orientation = float(angle if axis_a >= axis_b else angle + 90.0)
    else:
        (_, _), (rw, rh), angle = cv2.minAreaRect(contour)
        major = float(max(rw, rh))
        minor = float(min(rw, rh))
        orientation = float(angle)
    aspect = major / minor if minor > 0 else 999.0
    equivalent_diameter = math.sqrt(4.0 * area / math.pi) if area > 0 else 0.0
    mm = float(scale_px_per_mm)
    result = {
        'x': int(x), 'y': int(y), 'width': int(w), 'height': int(h),
        'centroid_x': round(cx, 3), 'centroid_y': round(cy, 3),
        'area_px2': round(area, 3), 'perimeter_px': round(perimeter, 3),
        'major_axis_px': round(major, 3), 'minor_axis_px': round(minor, 3),
        'aspect_ratio': round(aspect, 4), 'circularity': round(circularity, 4),
        'solidity': round(solidity, 4), 'extent': round(extent, 4),
        'convex_hull_area_px2': round(hull_area, 3),
        'equivalent_diameter_px': round(equivalent_diameter, 3),
        'orientation_deg': round(orientation % 180.0, 3),
    }
    if mm > 0:
        result.update({
            'area_mm2': round(area / (mm * mm), 5),
            'perimeter_mm': round(perimeter / mm, 5),
            'major_axis_mm': round(major / mm, 5),
            'minor_axis_mm': round(minor / mm, 5),
            'equivalent_diameter_mm': round(equivalent_diameter / mm, 5),
        })
    return result

def analyze(a):
    started = time.time()
    image = cv2.imread(a.input, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError('画像を読み込めません。')
    original_h, original_w = image.shape[:2]
    roi = None
    if a.roi_w > 0 and a.roi_h > 0:
        rx = max(0.0, min(1.0, float(a.roi_x)))
        ry = max(0.0, min(1.0, float(a.roi_y)))
        rw = max(0.0, min(1.0 - rx, float(a.roi_w)))
        rh = max(0.0, min(1.0 - ry, float(a.roi_h)))
        x1, y1 = int(round(rx * original_w)), int(round(ry * original_h))
        x2, y2 = int(round((rx + rw) * original_w)), int(round((ry + rh) * original_h))
        if x2 - x1 < 10 or y2 - y1 < 10:
            raise ValueError('ROIが小さすぎます。')
        image = image[y1:y2, x1:x2].copy()
        roi = {'x': x1, 'y': y1, 'width': x2 - x1, 'height': y2 - y1,
               'x_ratio': rx, 'y_ratio': ry, 'width_ratio': rw, 'height_ratio': rh}
    source_h, source_w = image.shape[:2]
    resize_scale = min(1.0, float(a.max_side) / max(source_h, source_w))
    if resize_scale < 1.0:
        image = cv2.resize(image, (int(round(source_w * resize_scale)), int(round(source_h * resize_scale))), interpolation=cv2.INTER_AREA)
    h, w = image.shape[:2]

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    raw_gray = gray.copy()
    if a.background_correction:
        bgk = odd(max(31, int(a.background_kernel)))
        background = cv2.GaussianBlur(gray, (bgk, bgk), 0)
        gray = cv2.divide(gray, np.maximum(background, 1), scale=255)
    if a.clahe:
        clahe = cv2.createCLAHE(clipLimit=float(a.clahe_clip), tileGridSize=(8, 8))
        gray = clahe.apply(gray)
    blurred = cv2.GaussianBlur(gray, (odd(a.blur), odd(a.blur)), 0)
    threshold_mode = cv2.THRESH_BINARY_INV if a.foreground == 'dark' else cv2.THRESH_BINARY
    if a.threshold_method == 'adaptive':
        block = odd(max(3, int(a.adaptive_block)))
        binary = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       threshold_mode, block, float(a.adaptive_c))
        threshold_value = -1.0
        threshold_source = 'adaptive'
    elif a.threshold < 0:
        threshold_value, binary = cv2.threshold(blurred, 0, 255, threshold_mode + cv2.THRESH_OTSU)
        threshold_source = 'otsu'
    else:
        threshold_value = float(a.threshold)
        _, binary = cv2.threshold(blurred, threshold_value, 255, threshold_mode)
        threshold_source = 'manual'
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (odd(a.morph_kernel), odd(a.morph_kernel)))
    if a.open_iterations > 0:
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=int(a.open_iterations))
    if a.close_iterations > 0:
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=int(a.close_iterations))

    distance_view = None
    watershed_view = None
    marker_count = 0
    if a.watershed:
        contours, distance_view, watershed_view, marker_count = contours_from_watershed(image, binary, a.distance_ratio, a.watershed_bg_iterations, a.peak_kernel)
    else:
        found = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = found[0] if len(found) == 2 else found[1]

    detections = []
    candidates = []
    rejected = {'area': 0, 'aspect': 0, 'solidity': 0, 'circularity': 0, 'extent': 0, 'border': 0}
    for contour in contours:
        # pixels_per_mm is calibrated against the uploaded original. Measurements
        # are performed after resizing, so the calibration must use the same scale.
        m = object_metrics(contour, a.pixels_per_mm * resize_scale)
        x, y, bw, bh = m['x'], m['y'], m['width'], m['height']
        if m['area_px2'] < a.min_area or m['area_px2'] > a.max_area:
            rejected['area'] += 1
            if m['area_px2'] >= max(10.0, a.min_area * 0.35):
                m['quality'] = 'candidate'
                m['quality_reasons'] = ['area']
                candidates.append((contour, m))
            continue
        failed = []
        if m['aspect_ratio'] > a.max_aspect: rejected['aspect'] += 1; failed.append('aspect')
        if m['solidity'] < a.min_solidity: rejected['solidity'] += 1; failed.append('solidity')
        if m['circularity'] < a.min_circularity or m['circularity'] > a.max_circularity: rejected['circularity'] += 1; failed.append('circularity')
        if m['extent'] < a.min_extent: rejected['extent'] += 1; failed.append('extent')
        if x <= a.border_margin or y <= a.border_margin or x + bw >= w - a.border_margin or y + bh >= h - a.border_margin:
            rejected['border'] += 1; continue
        m['quality'] = 'review' if failed else 'normal'
        m['quality_reasons'] = failed
        detections.append((contour, m))

    median_height = int(np.median([d[1]['height'] for d in detections])) if detections else 1
    detections.sort(key=lambda item: (item[1]['y'] // max(1, median_height), item[1]['x']))
    output = image.copy()
    for contour, m in candidates:
        cv2.drawContours(output, [contour], -1, (0, 0, 220), 2)
    rows = []
    for index, (contour, m) in enumerate(detections, 1):
        m['number'] = index
        rows.append(m)
        color = (0, 180, 0) if m['quality'] == 'normal' else (0, 190, 255)
        cv2.drawContours(output, [contour], -1, color, 2)
        x, y = m['x'], m['y']
        label = str(index)
        font_scale = max(0.42, min(0.76, m['width'] / 70.0))
        (tw, th), base = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 2)
        ty = max(th + base + 2, y - 4)
        cv2.rectangle(output, (x, ty - th - base - 2), (x + tw + 5, ty + 2), color, -1)
        cv2.putText(output, label, (x + 2, ty - base), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), 2, cv2.LINE_AA)

    if not cv2.imwrite(a.output, output, [int(cv2.IMWRITE_JPEG_QUALITY), 90]):
        raise IOError('結果画像を保存できません。')
    stage_files = {}
    if a.stage_dir:
        for name, stage in [('00_raw_gray', raw_gray), ('01_gray', gray), ('02_binary', binary), ('03_result', output)]:
            path = save_stage(a.stage_dir, name, stage)
            if path: stage_files[name] = path
        if distance_view is not None:
            path = save_stage(a.stage_dir, '04_distance', distance_view)
            if path: stage_files['04_distance'] = path
        if watershed_view is not None:
            path = save_stage(a.stage_dir, '05_watershed', watershed_view)
            if path: stage_files['05_watershed'] = path

    area_values = [r['area_px2'] for r in rows]
    major_values = [r['major_axis_px'] for r in rows]
    minor_values = [r['minor_axis_px'] for r in rows]
    circularity_values = [r['circularity'] for r in rows]
    solidity_values = [r['solidity'] for r in rows]
    summary = {
        'count': len(rows),
        'total_area_px2': round(sum(area_values), 3),
        'area_px2': stats(area_values),
        'major_axis_px': stats(major_values),
        'minor_axis_px': stats(minor_values),
        'circularity': stats(circularity_values),
        'solidity': stats(solidity_values),
    }
    if a.pixels_per_mm > 0:
        summary['area_mm2'] = stats([r['area_mm2'] for r in rows])
        summary['major_axis_mm'] = stats([r['major_axis_mm'] for r in rows])
        summary['minor_axis_mm'] = stats([r['minor_axis_mm'] for r in rows])

    return {
        'success': True,
        'count': len(rows),
        'processing_ms': int((time.time() - started) * 1000),
        'engine': {'python': platform.python_version(), 'opencv': cv2.__version__, 'numpy': np.__version__, 'algorithm_version': ALGORITHM_VERSION},
        'image': {'width_px': w, 'height_px': h, 'original_width_px': original_w, 'original_height_px': original_h, 'resize_scale': round(resize_scale, 6), 'roi': roi},
        'settings': {
            'threshold': round(float(threshold_value), 3), 'threshold_source': threshold_source,
            'threshold_method': a.threshold_method, 'background_correction': bool(a.background_correction),
            'background_kernel': a.background_kernel, 'adaptive_block': a.adaptive_block,
            'adaptive_c': a.adaptive_c, 'peak_kernel': a.peak_kernel,
            'foreground': a.foreground, 'min_area': a.min_area, 'max_area': a.max_area,
            'max_aspect': a.max_aspect, 'min_solidity': a.min_solidity,
            'min_circularity': a.min_circularity, 'max_circularity': a.max_circularity,
            'min_extent': a.min_extent, 'blur_size': odd(a.blur), 'morph_kernel': odd(a.morph_kernel),
            'open_iterations': a.open_iterations, 'close_iterations': a.close_iterations,
            'watershed_enabled': bool(a.watershed), 'distance_ratio': a.distance_ratio,
            'watershed_bg_iterations': a.watershed_bg_iterations, 'clahe_enabled': bool(a.clahe),
            'clahe_clip': a.clahe_clip, 'border_margin': a.border_margin,
            'max_side': a.max_side, 'pixels_per_mm': a.pixels_per_mm,
            'effective_pixels_per_mm': round(a.pixels_per_mm * resize_scale, 6),
            'roi_x': a.roi_x, 'roi_y': a.roi_y, 'roi_w': a.roi_w, 'roi_h': a.roi_h,
        },
        'watershed': {'marker_candidates': marker_count},
        'rejected': rejected,
        'summary': summary,
        'objects': rows,
        'candidate_count': len(candidates),
        'candidates': [m for _, m in candidates],
        'quality_counts': {'normal': sum(1 for r in rows if r['quality'] == 'normal'),
                           'review': sum(1 for r in rows if r['quality'] == 'review')},
        'stage_files': stage_files,
    }

def parser():
    p = argparse.ArgumentParser()
    p.add_argument('input', nargs='?'); p.add_argument('output', nargs='?')
    p.add_argument('--diagnose', action='store_true')
    p.add_argument('--stage-dir', default='')
    p.add_argument('--threshold', type=int, default=-1)
    p.add_argument('--threshold-method', choices=['otsu', 'manual', 'adaptive'], default='otsu')
    p.add_argument('--foreground', choices=['dark', 'light'], default='dark')
    p.add_argument('--min-area', type=float, default=100)
    p.add_argument('--max-area', type=float, default=12000)
    p.add_argument('--max-aspect', type=float, default=6)
    p.add_argument('--min-solidity', type=float, default=.55)
    p.add_argument('--min-circularity', type=float, default=.15)
    p.add_argument('--max-circularity', type=float, default=1.2)
    p.add_argument('--min-extent', type=float, default=.25)
    p.add_argument('--blur', type=int, default=5)
    p.add_argument('--morph-kernel', type=int, default=3)
    p.add_argument('--open-iterations', type=int, default=1)
    p.add_argument('--close-iterations', type=int, default=1)
    p.add_argument('--watershed', action='store_true')
    p.add_argument('--distance-ratio', type=float, default=.38)
    p.add_argument('--watershed-bg-iterations', type=int, default=2)
    p.add_argument('--clahe', action='store_true')
    p.add_argument('--clahe-clip', type=float, default=2.0)
    p.add_argument('--background-correction', action='store_true')
    p.add_argument('--background-kernel', type=int, default=101)
    p.add_argument('--adaptive-block', type=int, default=51)
    p.add_argument('--adaptive-c', type=float, default=5.0)
    p.add_argument('--peak-kernel', type=int, default=21)
    p.add_argument('--border-margin', type=int, default=2)
    p.add_argument('--max-side', type=int, default=2000)
    p.add_argument('--pixels-per-mm', type=float, default=0.0)
    p.add_argument('--roi-x', type=float, default=0.0)
    p.add_argument('--roi-y', type=float, default=0.0)
    p.add_argument('--roi-w', type=float, default=0.0)
    p.add_argument('--roi-h', type=float, default=0.0)
    return p

try:
    args = parser().parse_args()
    if args.diagnose:
        emit({'success': True, 'module': 'Seed Morphology Analyzer', 'python': platform.python_version(), 'opencv': cv2.__version__, 'numpy': np.__version__, 'algorithm_version': ALGORITHM_VERSION})
    elif not args.input or not args.output:
        raise ValueError('入力画像と出力画像を指定してください。')
    else:
        emit(analyze(args))
except Exception as exc:
    emit({'success': False, 'error': str(exc), 'error_type': type(exc).__name__})
    sys.exit(1)
