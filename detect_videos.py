import os
import csv
import cv2
import dlib
from concurrent.futures import ThreadPoolExecutor
import threading
from tqdm import tqdm
from main_module import (
    ensure_dir,
    visualize_facial_landmarks, 
    return_scaled_shape,
    detect_single_face,
    generate_landmark_headers
)


def process_video(video_path, output_dir, detector, predictor, save_raw=False, save_marked=False):

    video_name = os.path.splitext(os.path.basename(video_path))[0]
    raw_img_dir = os.path.join(output_dir, video_name) if save_raw else None
    marked_img_dir = os.path.join(output_dir, f"{video_name}_Marked") if save_marked else None

    for directory in [raw_img_dir, marked_img_dir]:
        if directory:
            ensure_dir(directory)

    csv_path = os.path.join(output_dir, f"{video_name}.csv")
    with open(csv_path, "w", newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(generate_landmark_headers("Video_Frame_Index"))

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
                cv2.imwrite(os.path.join(raw_img_dir, f"Frame_{count}.jpg"), image)

            # detect single face
            shape_np  = detect_single_face(image, detector, predictor)

            if shape_np is not None:

                # scale and extend shape
                scaled_shape = return_scaled_shape(shape_np)

                # Optional marked image
                if save_marked:
                    marked = visualize_facial_landmarks(image, scaled_shape)
                    cv2.imwrite(os.path.join(marked_img_dir, f"Marked_Frame_{count}.jpg"), marked)

                # Write csv data
                row = [coord for point in scaled_shape for coord in point]
                row.insert(0, count)
                writer.writerow(row)

            else:
                row = [count] + [""] * (len(generate_landmark_headers("Video_Frame_Index")) - 1)
                writer.writerow(row)

        pbar.close()


def process_all_videos(
    video_dir, 
    output_dir, 
    model_path,
    save_raw=False, 
    save_marked=False,
    video_filter='.mp4',
    max_workers=8
):
    ensure_dir(output_dir)

    video_files = sorted([
        os.path.join(video_dir, f) for f in os.listdir(video_dir) if f.endswith(video_filter)
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
