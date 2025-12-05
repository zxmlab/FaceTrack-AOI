import os
import math
import cv2
import numpy as np
import pandas as pd

# -------------------------
# Configuration
# -------------------------
REGIONS = [
    ("Jaw", 0, 17),
    ("RightEyebrow", 17, 22),
    ("LeftEyebrow", 22, 27),
    ("Nose", 27, 36),
    ("RightEye", 36, 42),
    ("LeftEye", 42, 48),
    ("Mouth", 48, 68),
    ("Face", 68, 72),
    ("Periocular", 72, 76),
    ("LeftScreen", 76, 80),    
    ("RightScreen", 80, 84),
    ("WholeScreen", 84, 88)
]

# region scaling factors (xs, ys)
REGION_PARAMS = {
    "RightEyebrow": (1.2, 1.2),
    "LeftEyebrow": (1.2, 1.2),
    "Nose": (2.0, 1.2),
    "RightEye": (1.8, 2.5),
    "LeftEye": (1.8, 2.5),
    "Mouth": (1.3, 1.2),
    "Face": (1.0, 1.0)
}

SCREEN_PARAMS = {
    "distance_mm": 600,    # distance in mm
    "screen_w_px": 1920,   # screen width in pixel
    "screen_h_px": 1080,   # screen height in pixel
    "screen_w_mm": 596,    # screen width in mm
    "screen_h_mm": 335     # screen height in mm
}

# colors: defined in RGB
_DEFAULT_COLORS_RGB = [
    (31, 119, 180),    # Jaw
    (255, 127, 14),    # RightEyebrow
    (44, 160, 44),     # LeftEyebrow
    (214, 39, 40),     # Nose
    (148, 103, 189),   # RightEye
    (140, 86, 75),     # LeftEye
    (255, 187, 120),   # Mouth
    (220, 220, 220),   # Face
    (255, 0, 255),     # Periocular
    (255, 215, 0),     # LeftScreen
    (0, 255, 255),     # RightScreen
    (135, 206, 250),   # WholeScreen
    (255, 105, 180),   # 
    (255, 0, 255),     # 
    (0, 255, 255),     # 
    (100, 100, 100),   # 
]

_DEFAULT_COLORS_BGR = [tuple(reversed(c)) for c in _DEFAULT_COLORS_RGB]

# -------------------------
# Utilities
# -------------------------
def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        print(f"Created directory: {path}")

def shape_to_numpy(shape):
    if isinstance(shape, np.ndarray):
        arr = shape.astype(float)
        if arr.ndim == 1 and arr.size == 136:
            arr = arr.reshape((-1, 2))
        return arr.copy()
    # try list-like
    try:
        flat = list(shape)
        if len(flat) == 136:
            return np.array(flat, dtype=float).reshape((-1, 2))
    except Exception:
        pass
    # dlib shape-like
    try:
        pts = np.array([[shape.part(i).x, shape.part(i).y] for i in range(68)], dtype=float)
        return pts
    except Exception:
        raise ValueError("Unsupported shape format. Expect dlib shape / (68,2) numpy / flat list of 136 numbers.")

def read_table_auto(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".csv":
        return pd.read_csv(path)
    else:
        return pd.read_csv(path, sep='\t', na_values='.')

def generate_landmark_headers(id_column):
    headers = [id_column]
    for name, start, end in REGIONS:
        for i in range(start, end):
            headers.extend([f"{name}_{i}_X", f"{name}_{i}_Y"])
    return headers

def generate_area_headers(id_column):
    headers = [id_column]
    for name, _, _ in REGIONS:
        headers.append(f"{name}_Area")
    return headers

# -------------------------
# Face Utilities
# -------------------------
def calculate_region_areas(shape_ext):
    """
    Return list of areas for each region (in pixel^2).
    """
    areas = []
    for name, start, end in REGIONS:
        pts = shape_ext[start:end].astype(np.float32)
        if pts.shape[0] >= 3:
            hull = cv2.convexHull(pts)
            area = cv2.contourArea(hull)
        else:
            area = 0.0
        areas.append(area)
    return areas

def detect_single_face(image, detector, predictor):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    rects = detector(gray, 1)

    if not rects:
        return None

    # selcct the largest face
    largest_rect = max(rects, key=lambda r: r.width() * r.height())
    shape = predictor(gray, largest_rect)
    shape_np = shape_to_numpy(shape)

    return shape_np

def in_bounds(x, y, bounds):
    if bounds is None or len(bounds) < 3:
        return False, 0
    bounds = bounds.copy()
    bounds = bounds.reshape((-1, 1, 2))
    hull = cv2.convexHull(bounds)
    area = cv2.contourArea(hull)
    inside = cv2.pointPolygonTest(hull, (x, y), False)
    return inside >= 0, area

def get_bounds(row, csv_source, key_column, index_column=None):
    key_value = row[key_column]
    bounds_dict = {}

    # Get Responding DataFrame
    if isinstance(csv_source, dict):
        df = csv_source.get(key_value)
        if df is None or df.empty:
            print(f"[Info] No matching landmark data for video '{key_value}'")
            return bounds_dict
        if index_column is not None:
            frame_index = row[index_column]
            matched_rows = df[df["Video_Frame_Index"] == frame_index]
            if matched_rows.empty:
                print(f"[Info] No matching landmark data for video '{key_value}', frame {int(frame_index)}")
                return bounds_dict
            match = matched_rows.iloc[0]
    else:
        df = csv_source
        matched_rows = df[df["Image_Name"] == key_value]
        if matched_rows.empty:
            print(f"[Info] No matching landmark data for image '{key_value}'")
            return bounds_dict
        match = matched_rows.iloc[0]

    # Extract coordinates for each region
    for region_name, start_idx, end_idx in REGIONS:
        xs, ys = [], []
        for i in range(start_idx, end_idx):
            x_col = f"{region_name}_{i}_X"
            y_col = f"{region_name}_{i}_Y"
            if x_col in df.columns and y_col in df.columns:
                x_val, y_val = match[x_col], match[y_col]
                if not (pd.isna(x_val) or pd.isna(y_val)):
                    xs.append(x_val)
                    ys.append(y_val)

        if xs and ys:
            coords = np.column_stack((xs, ys))
            bounds_dict[region_name] = coords
        else:
            print(f"[Info] Missing data for region '{region_name}' in '{key_value}'")

    return bounds_dict

def evaluate_fixation_regions(df, csv_source, fix_x_column, fix_y_column, key_column, index_column=None):
    region_names = [name for name, _, _ in REGIONS] + ["NonFace"]

    for region in region_names:
        df[f'CURRENT_IA_{region}'] = 0
    for region in region_names[:-1]:
        df[f'CURRENT_Area_{region}'] = 0.0

    for idx, row in df.iterrows():
        try:
            x, y = row[fix_x_column], row[fix_y_column]
            if pd.isna(x) or pd.isna(y):
                continue

            x, y = int(round(float(x))), int(round(float(y)))

            bounds_dict = get_bounds(row, csv_source, key_column, index_column)

            for region in region_names[:-1]:  # except for NonFace
                region_bounds = bounds_dict.get(region)
                if region_bounds is None:
                    continue
                region_bounds = np.array(region_bounds, dtype=np.float32)
                inside, area = in_bounds(x, y, region_bounds)
                df.at[idx, f'CURRENT_Area_{region}'] = area
                if inside:
                    df.at[idx, f'CURRENT_IA_{region}'] = 1

            # NonFace
            if 'CURRENT_IA_WholeScreen' in df.columns and 'CURRENT_IA_Face' in df.columns:
                if df.at[idx, 'CURRENT_IA_WholeScreen'] and not df.at[idx, 'CURRENT_IA_Face']:
                    df.at[idx, 'CURRENT_IA_NonFace'] = 1

        except Exception as e:
            print(f"[Error] Processing row {idx}: {e}\n")

    return df

# -------------------------
# Extended shape builder
# -------------------------
def build_extended_shape(shape68):
    if shape68.shape[0] < 68:
        raise ValueError("Input must have at least 68 landmarks.")
    base = shape68[:68].astype(float)

    # compute face bbox
    x_min_all, y_min_all = np.min(base[:, 0]), np.min(base[:, 1])
    x_max_all, y_max_all = np.max(base[:, 0]), np.max(base[:, 1])
    jaw = base[0:17]
    jaw_h = np.max(jaw[:, 1]) - np.min(jaw[:, 1])

    # expand top of face by one jaw height to include forehead (approx)
    y_min_face = max(0.0, np.min(jaw[:, 1]) - jaw_h)
    face_rect = np.array([
        [x_min_all, y_min_face],
        [x_max_all, y_min_face],
        [x_max_all, y_max_all],
        [x_min_all, y_max_all]
    ], dtype=float)

    # assemble final pts
    extended = np.zeros((REGIONS[-1][-1], 2), dtype=float)
    extended[0:68] = base
    extended[68:72] = face_rect

    return extended

# -------------------------
# Scaling functions
# -------------------------
def scale_shape(region_points, xscale, yscale):
    """
    Scale an array of points (n,2) around its centroid.
    Defensive: if width/height is 0, fallback to scaling about centroid without dividing by zero.
    Returns new numpy array float.
    """
    pts = np.array(region_points, dtype=float)
    if pts.size == 0:
        return pts
    cx, cy = np.mean(pts, axis=0)
    # apply
    new = pts.copy()
    new[:, 0] = xscale * (pts[:, 0] - cx) + cx
    new[:, 1] = yscale * (pts[:, 1] - cy) + cy
    return new

def enlarge_shape_by_degree(region_points, add_deg_x, add_deg_y):
    """
    Enlarge a region by visual angle (degrees) mapped to pixels.
    add_deg_x / add_deg_y are degrees to add to region width/height.
    """
    distance_mm = SCREEN_PARAMS["distance_mm"]
    screen_w_px = SCREEN_PARAMS["screen_w_px"]
    screen_h_px = SCREEN_PARAMS["screen_h_px"]
    screen_w_mm = SCREEN_PARAMS["screen_w_mm"]
    screen_h_mm = SCREEN_PARAMS["screen_h_mm"]

    pts = np.array(region_points, dtype=float)
    if pts.shape[0] == 0:
        return pts

    # region bbox
    x_min, y_min = np.min(pts[:, 0]), np.min(pts[:, 1])
    x_max, y_max = np.max(pts[:, 0]), np.max(pts[:, 1])
    orig_w = x_max - x_min
    orig_h = y_max - y_min

    # map degrees to mm -> pixels
    delta_x_mm = (math.tan(math.radians(add_deg_x) / 2.0) * distance_mm) * 2.0
    delta_y_mm = (math.tan(math.radians(add_deg_y) / 2.0) * distance_mm) * 2.0
    delta_x_px = delta_x_mm * (screen_w_px / screen_w_mm)
    delta_y_px = delta_y_mm * (screen_h_px / screen_h_mm)

    # avoid division by zero
    if orig_w <= 1e-6:
        xscale = 1.0
    else:
        xscale = (orig_w + delta_x_px) / orig_w

    if orig_h <= 1e-6:
        yscale = 1.0
    else:
        yscale = (orig_h + delta_y_px) / orig_h

    return scale_shape(pts, xscale, yscale)

# -------------------------
# High-level pipeline
# -------------------------
def return_scaled_shape(shape_input, use_degree=False, region_params=None):

    if region_params is None:
        region_params = REGION_PARAMS

    shape_arr = shape_to_numpy(shape_input)
    if shape_arr.shape[0] == 68:
        shape_ext = build_extended_shape(shape_arr)
        out = shape_ext.copy()
    elif shape_arr.shape[0] == REGIONS[-1][-1]:
        out = shape_arr.copy()
    else:
        print(f"Shape need to be {REGIONS[-1][-1]} points.")

    # iterate over regions and write into out[start:end] 
    skip_regions = {"Periocular", "LeftScreen", "RightScreen", "WholeScreen"}
    for name, start, end in REGIONS:

        # skip special-case composite regions for now
        if name in skip_regions:
            continue

        if name in region_params:
            a, b = region_params[name]
            pts = out[start:end]
            if use_degree:
                newpts = enlarge_shape_by_degree(pts, a, b)
            else:
                newpts = scale_shape(pts, a, b)

            # protect shape size mismatch: ensure newpts shape matches (end-start)
            if newpts.shape[0] == (end - start):
                out[start:end] = newpts
            else:
                # if not equal (rare), try to interpolate/backfill or center-scale bounding box
                # fallback: compute scaled bbox centered at centroid
                cen = pts.mean(axis=0)
                offsets = pts - cen
                out[start:end] = cen + offsets * np.array([a, b])

    # Precompute face box mids
    screen_w_px = SCREEN_PARAMS["screen_w_px"]
    screen_h_px = SCREEN_PARAMS["screen_h_px"]

    # special-case composite regions
    for name, start, end in REGIONS:
        if name == "Periocular":
            r_eyebrow = out[17:22]
            l_eyebrow = out[22:27]
            r_eye = out[36:42]
            l_eye = out[42:48]
            periocular_stack = np.vstack([r_eyebrow, l_eyebrow, r_eye, l_eye])
            x_min_p, y_min_p = np.min(periocular_stack[:, 0]), np.min(periocular_stack[:, 1])
            x_max_p, y_max_p = np.max(periocular_stack[:, 0]), np.max(periocular_stack[:, 1])
            out[start:end] = np.array([
                [x_min_p, y_min_p],
                [x_max_p, y_min_p],
                [x_max_p, y_max_p],
                [x_min_p, y_max_p]
            ], dtype=float)

        elif name == "LeftScreen":
            out[start:end] = np.array([
                [0, 0],
                [screen_w_px / 2, 0],
                [screen_w_px / 2, screen_h_px],
                [0, screen_h_px]
            ], dtype=float)

        elif name == "RightScreen":
            out[start:end] = np.array([
                [screen_w_px / 2, 0],
                [screen_w_px, 0],
                [screen_w_px, screen_h_px],
                [screen_w_px / 2, screen_h_px]
            ], dtype=float)

        elif name == "WholeScreen":
            out[start:end] = np.array([
                [0, 0],
                [screen_w_px, 0],
                [screen_w_px, screen_h_px],
                [0, screen_h_px]
            ], dtype=float)

    return out

# -------------------------
# Visualization
# -------------------------
def visualize_facial_landmarks(image, shape_ext, colors=None, alpha=0.5, point_radius=2):

    if colors is None:
        colors = _DEFAULT_COLORS_BGR
    if len(colors) < len(REGIONS):
        raise ValueError("colors list too short")

    out_img = image.copy()
    h, w = image.shape[:2]

    for idx, (name, start, end) in enumerate(REGIONS):
        pts = shape_ext[start:end].astype(np.int32)
        mask = np.zeros_like(out_img, dtype=np.uint8)

        if name == "Jaw":
            # draw polyline
            for i in range(1, len(pts)):
                cv2.line(mask, tuple(pts[i-1]), tuple(pts[i]), colors[idx], thickness=2)
        elif name == "Face":
            # draw rectangle outline
            cv2.rectangle(mask, tuple(pts[0]), tuple(pts[2]), colors[idx], thickness=2)
        elif name == "Periocular":
            cv2.rectangle(mask, tuple(pts[0]), tuple(pts[2]), colors[idx], thickness=2)
            # pass
        elif name in ["LeftScreen", "RightScreen", "WholeScreen"]:
            # cv2.rectangle(mask, tuple(pts[0]), tuple(pts[2]), (0, 0, 255), thickness=2)
            pass
        else:
            # general: filled convex hull
            if pts.shape[0] >= 3:
                hull = cv2.convexHull(pts)
                cv2.drawContours(mask, [hull], -1, colors[idx], thickness=2)
            else:
                # fallback: draw small circles
                for p in pts:
                    cv2.circle(mask, tuple(p), radius=point_radius, color=colors[idx], thickness=-1)

        # blend
        out_img = cv2.addWeighted(out_img, 1.0, mask, alpha, 0)

        # optionally draw point centers (contrasting color)
        for p in pts:
            cv2.circle(out_img, tuple(p), radius=point_radius, color=(0, 0, 255), thickness=-1)

    return out_img
