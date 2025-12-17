import pandas as pd
import os
from main_module import ensure_dir, read_table_auto, evaluate_fixation_regions

def process_fixation_video(
        input_path, 
        csvtable_dir, 
        fix_x_column = "CURRENT_FIX_X",
        fix_y_column = "CURRENT_FIX_Y",
        video_name_column = "VIDEO_NAME_END",
        frame_index_column = "VIDEO_FRAME_INDEX_END",
        video_filter='.mp4',
        output_path=None,
        ):

    print(f"Reading data from: {input_path}")
    df = read_table_auto(input_path)

    unique_video_names = df[
        df[video_name_column].notna() & df[video_name_column].str.endswith(video_filter)
        ][video_name_column].unique()

    csv_data = {}
    for video_name in unique_video_names:
        csv_name = video_name.replace(video_filter, '.csv')
        csv_path = os.path.join(csvtable_dir, csv_name)
        try:
            csv_data[video_name] = pd.read_csv(csv_path)
        except FileNotFoundError:
            print(f"[Warning] CSV landmark file not found: {video_name}")

    print("Evaluating fixation regions...")
    df = evaluate_fixation_regions(df, csv_data, fix_x_column, fix_y_column, 
                                   video_name_column, frame_index_column)

    if output_path:
        output_dir = os.path.dirname(output_path)
        if output_dir:
            ensure_dir(output_dir)

        df.to_csv(output_path, index=False)
        print(f"Output saved to: {output_path}")
    else:
        print("No output path provided, returning DataFrame.")

    return df
