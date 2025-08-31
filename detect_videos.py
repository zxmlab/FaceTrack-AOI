import os
import csv
import cv2
import dlib
from concurrent.futures import ThreadPoolExecutor
import threading
from tqdm import tqdm
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
    headers = ["Video_Frame_Index"]
    for name, start, end in regions:
        for i in range(start, end):
            headers.extend([f"{name}_{i}_X", f"{name}_{i}_Y"])
    return headers


def process_video(video_path, output_dir, detector, predictor, save_raw=False, save_marked=False):
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    raw_img_dir = os.path.join(output_dir, video_name) if save_raw else None
    marked_img_dir = os.path.join(output_dir, f"{video_name}_Marked") if save_marked else None

    for directory in [raw_img_dir, marked_img_dir]:
        if directory:
            create_output_dir(directory)

    csv_path = os.path.join(output_dir, f"{video_name}.csv")
    with open(csv_path, "w", newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(generate_landmark_headers())

        vidcap = cv2.VideoCapture(video_path)
        total_frames = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
        count = 0

        pbar = tqdm(total=total_frames, desc=f"{video_name}", position=0, leave=False)

        while True:
            success, image = vidcap.read()
            if not success:
                break

            count += 1
            pbar.update(1)

            if save_raw:
                cv2.imwrite(os.path.join(raw_img_dir, f"frame{count}.jpg"), image)

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            rects = detector(gray, 1)

            if rects:
                largest_rect = max(rects, key=lambda r: r.width() * r.height())
                shape = predictor(gray, largest_rect)
                shape_np = shape_to_numpy_array(shape)

                if save_marked:
                    marked = visualize_facial_landmarks(image, shape_np)
                    cv2.imwrite(os.path.join(marked_img_dir, f"Marked_frame{count}.jpg"), marked)

                row = shape_to_list(shape)
                row.insert(0, count)
                writer.writerow(row)

        pbar.close()


def process_all_videos(
    video_dir, 
    output_dir, 
    model_path,
    save_raw=False, 
    save_marked=False, 
    max_workers=8
):
    create_output_dir(output_dir)

    video_files = sorted([
        os.path.join(video_dir, f) for f in os.listdir(video_dir) if f.endswith(".mp4")
    ])

    thread_local = threading.local()

    def get_detector():
        if not hasattr(thread_local, "detector"):
            thread_local.detector = dlib.get_frontal_face_detector()
        return thread_local.detector

    def get_predictor():
        if not hasattr(thread_local, "predictor"):
            thread_local.predictor = dlib.shape_predictor(model_path)
        return thread_local.predictor

    def process_wrapper(video_file):
        detector = get_detector()
        predictor = get_predictor()
        process_video(video_file, output_dir, detector, predictor, save_raw, save_marked)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        list(executor.map(process_wrapper, video_files))
