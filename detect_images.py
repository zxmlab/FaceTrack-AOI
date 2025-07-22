import os
import csv
import cv2
import dlib
from main_module import shape_to_list, visualize_facial_landmarks, shape_to_numpy_array


def create_output_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Created directory: {path}")
    else:
        print(f"Directory already exists: {path}")


def generate_landmark_headers():
    regions = [
        ("Jaw", 0, 17),
        ("Right_Eyebrow", 17, 22),
        ("Left_Eyebrow", 22, 27),
        ("Nose", 27, 36),
        ("Right_Eye", 36, 42),
        ("Left_Eye", 42, 48),
        ("Mouth", 48, 68)
    ]
    headers = ["Image_Name"]
    for name, start, end in regions:
        for i in range(start, end):
            headers.extend([f"{name}_{i}_X", f"{name}_{i}_Y"])
    return headers


def process_images(
    image_dir,
    output_dir,
    model_path,
    save_marked=False
):
    create_output_dir(output_dir)
    marked_dir = os.path.join(output_dir, "Marked") if save_marked else None
    if marked_dir:
        create_output_dir(marked_dir)

    # Load detector and predictor
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(model_path)

    # Output CSV path
    all_csv_path = os.path.join(output_dir, "all_landmarks.csv")

    # Write header once
    with open(all_csv_path, "w", newline='') as all_csvfile:
        writer = csv.writer(all_csvfile, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(generate_landmark_headers())

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

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            rects = detector(gray, 1)

            if len(rects) == 0:
                print(f"No face detected in: {filename}")
                continue

            shape = predictor(gray, rects[0])
            landmarks = shape_to_list(shape)

            # Optional marked image
            if save_marked:
                shape_np = shape_to_numpy_array(shape)
                marked = visualize_facial_landmarks(image, shape_np)
                cv2.imwrite(os.path.join(marked_dir, filename), marked)

            # Write row: [filename, landmark1_x, landmark1_y, ..., landmark68_x, landmark68_y]
            writer.writerow([filename] + landmarks)

            print(f"Processed: {filename}")
