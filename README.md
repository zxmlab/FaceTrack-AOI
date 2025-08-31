## Project Overview

This project presents a modular toolkit for facial landmark detection and fixation analysis across both image and video formats. Designed with cognitive and behavioral research in mind—such as face perception, eye-tracking analysis, and attention modeling—the toolkit enables researchers to extract precise facial feature coordinates and compare them to gaze fixation data. The modular structure supports extensibility, batch processing, and integration into experimental pipelines.

Eye-tracking studies involving human faces often require region-specific fixation analysis—e.g., determining whether fixations fall within the eyes, nose, or mouth. However, raw fixation coordinates are typically collected independently of facial feature segmentation. This toolkit bridges that gap by providing an automated pipeline to detect facial landmarks and compare them to fixation data on a frame-by-frame or image-by-image basis.

The toolkit uses Dlib’s 68-point facial landmark model, which offers a balance between precision and computational cost. This makes it suitable for large-scale studies involving naturalistic stimuli such as social videos or spontaneous facial expressions.

At present, the tool can only handle stimuli with a single face. In cases with multiple faces, it selects only the largest one.

## System Architecture

The system is divided into five major functional modules:

1. **Facial Landmark Detection in Videos**
2. **Facial Landmark Detection in Images**
3. **Fixation Comparison in Videos**
4. **Fixation Comparison in Images**
5. **Annotated Video Generation with Facial Features**

Each module is implemented as an independent component but shares a consistent internal pipeline. All landmark detection operations are built on top of Dlib’s face detector and shape predictor, while video I/O tasks rely on OpenCV.

## Input and Output Formats

### Facial Landmark CSV Files

- **Input**: Video or image files
- **Output**: A `.csv` file per video or a combined `.csv` for images
- **Fields**: Frame index (or image name), coordinates of each facial landmark point

### Fixation Data Format

- **Required Fields**:
  - `VIDEO_NAME_END` or `IMAGE_NAME_END`: filename reference
  - `VIDEO_FRAME_INDEX_END`: (for video) specifies the frame to match
  - `x`, `y`: fixation coordinate in pixels
- **Output: New columns are added to fixation data**:
  - `CURRENT_IA_<region>`: binary indicator (1 = inside region, 0 = outside)
  - `CURRENT_Area_<region>`: pixel area of the region

## Algorithmic Details

### Facial Landmark Detection

Facial landmarks are extracted using the `shape_predictor_68_face_landmarks.dat` model, which returns 68 canonical points covering the jawline, eyebrows, eyes, nose, and mouth.

### Region Construction

Since the predictor does not return a full-face bounding box, the jaw region is used to estimate facial boundaries. The minimal enclosing rectangle of the jaw is extended vertically to include upper facial regions. Additional bounding boxes are generated around each region of interest using empirically chosen amplification factors:

| Region   | X-axis Amplification | Y-axis Amplification |
| -------- | -------------------- | -------------------- |
| Eyebrows | 1.2                  | 1.2                  |
| Eyes     | 1.5                  | 2.0                  |
| Nose     | 2.0                  | 1.2                  |
| Mouth    | 1.3                  | 1.2                  |

These values can be configured in the `main_module.py` to suit different datasets.

### Fixation Comparison

Each fixation coordinate is compared against the bounding box of each facial region. Binary inclusion results are recorded, and pixel areas of the regions are calculated for further analysis (e.g., area normalization of fixation counts).

## Annotated Video Generation

The `process_videos` function enables the generation of videos with overlaid facial landmarks. It leverages OpenCV’s `cv2.VideoWriter` to write frame-by-frame annotated outputs. Multithreading is supported via the `max_workers` parameter to facilitate parallel processing of video batches.

## Technical Dependencies

- **Programming Language**: Python 3.7+
- **Libraries**:
  - `numpy`
  - `opencv-python`
  - `dlib`
  - `pandas`
  - `tqdm` (for progress monitoring)
  - `moviepy`
  - `kivy`
- **Pre-trained Model**: `shape_predictor_68_face_landmarks.dat` (Dlib)

All required libraries can be installed via `pip`, and the model can be downloaded from the official Dlib repository.

## Example Usage

### Video Stimuli for EyeLink Experiment

1. Detect Facial Landmarks

```python
from detect_videos import process_all_videos

process_all_videos(
    video_dir = "./videos",
    output_dir = "./videos/output",
    model_path = "./model/shape_predictor_68_face_landmarks.dat",
    save_raw = True,
    save_marked = True
)
```

2. Compare Fixations to Facial Regions

```python
from comparision_fixation_videos_eyelink import process_fixation_video

process_fixation_video(
    input_txt_path = "./video_fixation_data.txt",
    input_CSVtable_dir = "./videos/output",
    videofilter = ".mp4",
    output_csv_path = "./output/output_video_fixation_data.csv"
)
```

### Image Stimuli for EyeLink Experiment

1. Detect Facial Landmarks

```python
from detect_images import process_images

process_images(
    image_dir = "./images",
    output_dir = "./images/output",
    model_path = "./model/shape_predictor_68_face_landmarks.dat",
    save_marked = True
)
```

2. Compare Fixations to Facial Regions

```python
from comparision_fixation_images_eyelink import process_fixation_image

process_fixation_image(
    input_txt_path = "./fixation_data.txt",
    csvtable_path = "./images/output/all_landmarks.csv",
    imagecolumn = "image_column",
    output_path = "./output/output_fixation_data.csv",
)
```

### Image Stimuli for Tobii Experiment

1. Detect Facial Landmarks

```python
from detect_images import process_images

process_images(
    image_dir = "./images",
    output_dir = "./images/output",
    model_path = "./model/shape_predictor_68_face_landmarks.dat",
    save_marked = True
)
```

2. Compare Fixations to Facial Regions

```python
from comparision_fixation_images_tobii import process_fixation_image

process_fixation_image(
    input_folder = "./fixation_data",
    output_folder = "./fixation_data/output",
    csvtable_path = "./images/output/all_landmarks.csv",
    imagecolumn = "Presented Media name"
)
```

### Generate Annotated Videos

```python
from facial_video_processor import process_videos

process_videos(
    video_dir = "./videos",
    output_dir = "./videos/annotated_videos",
    model_path = "./shape_predictor_68_face_landmarks.dat",
    max_workers = 4
)
```

## Citation

To be done.

