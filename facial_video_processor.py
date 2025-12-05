import os
import cv2
import dlib
from moviepy.editor import VideoFileClip
from tqdm import tqdm
import concurrent.futures
from main_module import shape_to_numpy, visualize_facial_landmarks, return_scaled_shape


def ensure_trailing_slash(path: str) -> str:
    return path if path.endswith("/") else path + "/"


def setup_output_directory(output_dir: str) -> None:
    os.makedirs(output_dir, exist_ok=True)
    print(f"[INFO] Output directory ready: {output_dir}")


def load_dlib_models(model_path: str = None):
    if model_path is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(base_dir, 'model/shape_predictor_68_face_landmarks.dat')

    if not os.path.isfile(model_path):
        raise FileNotFoundError(f"[ERROR] Model file not found at: {model_path}")

    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(model_path)
    return detector, predictor


def make_image_processor(detector, predictor):
    def process_image(image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        rects = detector(gray, 1)
        for rect in rects:
            shape_np = shape_to_numpy(predictor(gray, rect))
            scaled_shape = return_scaled_shape(shape_np)
            return visualize_facial_landmarks(image.copy(), scaled_shape)
        return image  # Return original if no face detected
    return process_image


def process_single_video(video_file, video_dir, output_dir, model_path):
    import multiprocessing

    video_path = os.path.join(video_dir, video_file)
    output_path = os.path.join(output_dir, f"Masked_{video_file}")

    print(f"[INFO] Start processing {video_file} in process {multiprocessing.current_process().pid}")

    detector, predictor = load_dlib_models(model_path)
    process_image = make_image_processor(detector, predictor)

    try:
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        count = 0

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        pbar = tqdm(total=total_frames, desc=f"{video_file}", position=0, leave=False)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            count += 1
            pbar.update(1)
            processed = process_image(frame)
            writer.write(processed)

        cap.release()
        writer.release()
        pbar.close()

        print(f"[INFO] Saved processed video to: {output_path}")

    except Exception as e:
        print(f"[ERROR] Failed to process {video_file}: {e}")


def process_videos(video_dir: str, output_dir: str, model_path: str = None, max_workers: int = 2) -> None:
    video_dir = ensure_trailing_slash(video_dir)
    output_dir = ensure_trailing_slash(output_dir)
    setup_output_directory(output_dir)

    video_files = sorted(f for f in os.listdir(video_dir) if f.endswith(".mp4"))

    if not video_files:
        print(f"[WARNING] No .mp4 files found in directory: {video_dir}")
        return

    print(f"[INFO] Found {len(video_files)} videos. Starting parallel processing...")

    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for video_file in video_files:
            futures.append(executor.submit(process_single_video, video_file, video_dir, output_dir, model_path))

        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as exc:
                print(f"[ERROR] Video {video_file} processing generated an exception: {exc}")
