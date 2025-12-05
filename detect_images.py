import os
import csv
import cv2
import dlib
from main_module import (
    ensure_dir,
    visualize_facial_landmarks, 
    return_scaled_shape,
    detect_single_face,
    calculate_region_areas,
    generate_landmark_headers,
    generate_area_headers
)

def process_images(image_dir, output_dir, model_path, save_marked=False):

    ensure_dir(output_dir)
    marked_dir = os.path.join(output_dir, "Marked") if save_marked else None
    if marked_dir:
        ensure_dir(marked_dir)

    # Load detector and predictor
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(model_path)

    # Output CSV path
    coords_csv_path = os.path.join(output_dir, "landmarks.csv")
    area_csv_path = os.path.join(output_dir, "areas.csv")

    # Write header once
    with open(coords_csv_path, "w", newline='') as coords_file, \
         open(area_csv_path, "w", newline='') as area_file:
        
        coords_writer = csv.writer(coords_file, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
        area_writer = csv.writer(area_file, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)

        coords_writer.writerow(generate_landmark_headers("Image_Name"))
        area_writer.writerow(generate_area_headers("Image_Name"))

        # Process all images
        image_files = sorted([
            f for f in os.listdir(image_dir)
            if f.lower().endswith(('.jpg', '.jpeg', '.png'))
        ])

        for filename in image_files:
            image_path = os.path.join(image_dir, filename)
            image = cv2.imread(image_path)

            if image is None:
                print(f"Failed to load image: {filename}")
                continue

            # detect single face
            shape_np  = detect_single_face(image, detector, predictor)
            if shape_np is None:
                print(f"No face detected in: {filename}")
                continue

            # scale and extend shape
            scaled_shape = return_scaled_shape(shape_np)

            # calculate region areas
            region_areas = calculate_region_areas(scaled_shape)

            # Optional marked image
            if save_marked:
                marked = visualize_facial_landmarks(image, scaled_shape)
                cv2.imwrite(os.path.join(marked_dir, filename), marked)

            # Write Coordinates
            coords_row = [filename] + [coord for point in scaled_shape for coord in point]
            coords_writer.writerow(coords_row)

            # Write Area
            area_row = [filename] + region_areas
            area_writer.writerow(area_row)

            print(f"Processed: {filename}")
