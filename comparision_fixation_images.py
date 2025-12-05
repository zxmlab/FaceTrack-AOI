import pandas as pd
import os
from main_module import ensure_dir, read_table_auto, evaluate_fixation_regions

def process_fixation_image(
        input_path,
        csvtable_path,
        image_column,
        fix_x_column="CURRENT_FIX_X",
        fix_y_column="CURRENT_FIX_Y",
        output_path=None, 
        ):
    
    print(f"Reading fixation data from: {input_path}")
    df = read_table_auto(input_path)
    csv_table = pd.read_csv(csvtable_path)

    print("Evaluating fixation regions...")
    df = evaluate_fixation_regions(df, csv_table, fix_x_column, fix_y_column, image_column)

    if output_path:
        output_dir = os.path.dirname(output_path)
        if output_dir:
            ensure_dir(output_dir)

        df.to_csv(output_path, index=False)
        print(f"Output saved to: {output_path}")
    else:
        print("No output path provided, returning DataFrame.")

    return df
