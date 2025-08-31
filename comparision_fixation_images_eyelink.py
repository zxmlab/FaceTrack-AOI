import pandas as pd
import numpy as np
import cv2
import os
from main_module import scale_shape, region_params


def in_bounds(x, y, bounds, y_adjust, xscale=1.0, yscale=1.0):
    if bounds is None or len(bounds) < 3:
        return False, 0
    bounds = bounds.copy()
    bounds[::, 1] += y_adjust  # Adjust for y-axis
    bounds = scale_shape(bounds, xscale, yscale)
    bounds = bounds.reshape((-1, 1, 2))
    area = cv2.contourArea(bounds)
    inside = cv2.pointPolygonTest(bounds, (x, y), False)
    return inside >= 0, area


def get_bounds_from_row(row, csv_table, imagecolumn):
    image_name = row[imagecolumn]
    bounds_dict = {}

    image_df = csv_table[csv_table["Image_Name"] == image_name]
    if image_df is not None:
        match = image_df.to_numpy()
        if match.size:
            Jaw_X = match[0, range(1, 34, 2)]
            Jaw_Y = match[0, range(2, 35, 2)]
            min_Jaw_X, max_Jaw_X = min(Jaw_X), max(Jaw_X)
            min_Jaw_Y, max_Jaw_Y = min(Jaw_Y), max(Jaw_Y)
            min_Jaw_Y = min_Jaw_Y - (max_Jaw_Y - min_Jaw_Y)
            bounds_Face = np.array(
                [min_Jaw_X, min_Jaw_Y, min_Jaw_X, max_Jaw_Y, max_Jaw_X, max_Jaw_Y, max_Jaw_X, min_Jaw_Y]
            ).reshape((4, 2))

            bounds = {
                "Jaw": (range(1, 35), 17),
                "RightEyebrow": (range(35, 45), 5),
                "LeftEyebrow": (range(45, 55), 5),
                "Nose": (range(55, 73), 9),
                "RightEye": (range(73, 85), 6),
                "LeftEye": (range(85, 97), 6),
                "Mouth": (range(97, 137), 20)
            }

            bounds_dict = {
                name: np.array(match[0, idx_range]).reshape((num_points, 2))
                for name, (idx_range, num_points) in bounds.items()
            }

            bounds_dict["Face"] = bounds_Face
        else:
            print(f"[Info] No matching landmark data for image '{image_name}'")

    return bounds_dict


def evaluate_fixation_regions(df, csv_table, imagecolumn, y_adjust):
    regions = ["Face", "LeftEyebrow", "RightEyebrow", "LeftEye", "RightEye", "Nose", "Mouth", "NonFace"]
    for region in regions:
        df[f'CURRENT_IA_{region}'] = 0

    for region in regions[:-1]:
        df[f'CURRENT_Area_{region}'] = 0.0

    for idx, row in df.iterrows():
        x, y = row['CURRENT_FIX_X'], row['CURRENT_FIX_Y']
        if pd.isna(x) or pd.isna(y):
            continue

        try:
            x, y = int(round(float(x))), int(round(float(y)))
            bounds_dict = get_bounds_from_row(row, csv_table, imagecolumn)
            inside_any = False

            for region, xscale, yscale in region_params:
                region_bounds = bounds_dict.get(region)
                region_bounds = np.array(region_bounds, dtype=np.int32)
                if region_bounds is not None:
                    inside, area = in_bounds(x, y, region_bounds, y_adjust, xscale, yscale)
                    df.at[idx, f'CURRENT_Area_{region}'] = area
                    if inside:
                        df.at[idx, f'CURRENT_IA_{region}'] = 1
                        inside_any = True

            if not inside_any:
                df.at[idx, 'CURRENT_IA_NonFace'] = 1

        except Exception as e:
            print(f"[Error] Processing row {idx}: {e}\n")

    return df


def process_fixation_image(input_txt_path, csvtable_path, imagecolumn, output_path=None, y_adjust=60):
    print(f"Reading fixation data from: {input_txt_path}")
    df = pd.read_csv(input_txt_path, sep='\t', na_values='.')
    csv_table = pd.read_csv(csvtable_path)

    print("Evaluating fixation regions...")
    df = evaluate_fixation_regions(df, csv_table, imagecolumn, y_adjust)

    if output_path:
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            print(f"Created output directory: {output_dir}")

        df.to_csv(output_path, index=False)
        print(f"Output saved to: {output_path}")
    else:
        print("No output path provided, returning DataFrame.")

    return df
