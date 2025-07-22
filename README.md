# FaceTrack-AOI
An AI-Driven Tool for Automated Dynamic AOI Placement and Gaze Analysis in Facial Learning Studies


## Project Overview

This project presents a modular toolkit for facial landmark detection and fixation analysis across both image and video formats. Designed with cognitive and behavioral research in mind—such as face perception, eye-tracking analysis, and attention modeling—the toolkit enables researchers to extract precise facial feature coordinates and compare them to gaze fixation data. The modular structure supports extensibility, batch processing, and integration into experimental pipelines.

## Motivation and Background

Eye-tracking studies involving human faces often require region-specific fixation analysis—e.g., determining whether fixations fall within the eyes, nose, or mouth. However, raw fixation coordinates are typically collected independently of facial feature segmentation. This toolkit bridges that gap by providing an automated pipeline to detect facial landmarks and compare them to fixation data on a frame-by-frame or image-by-image basis.

The toolkit uses Dlib’s 68-point facial landmark model, which offers a balance between precision and computational cost. This makes it suitable for large-scale studies involving naturalistic stimuli such as social videos or spontaneous facial expressions.

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

### Output (After Fixation Comparison)

- New columns are added to fixation data:
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

These values can be configured in the source code to suit different datasets.

### Fixation Comparison

Each fixation coordinate is compared against the bounding box of each facial region. Binary inclusion results are recorded, and pixel areas of the regions are calculated for further analysis (e.g., area normalization of fixation counts).

## Annotated Video Generation

The `process_videos` function enables the generation of videos with overlaid facial landmarks. It leverages OpenCV’s `cv2.VideoWriter` to write frame-by-frame annotated outputs. Multithreading is supported via the `max_workers` parameter to facilitate parallel processing of video batches.

## Technical Dependencies

- **Programming Language**: Python 3.7+
- **Libraries**:
  - `dlib`
  - `opencv-python`
  - `numpy`
  - `pandas`
  - `tqdm` (for progress monitoring)
- **Pre-trained Model**: `shape_predictor_68_face_landmarks.dat` (Dlib)

All required libraries can be installed via `pip`, and the model can be downloaded from the official Dlib repository.

## Performance and Scalability

- Batch processing of video/image directories is supported.
- Multithreading via Python’s `concurrent.futures` significantly improves processing speed for large datasets.
- Lightweight and portable; does not require GPU.

## Customization and Extensibility

- Region amplification factors are modifiable to adapt to various experimental setups.
- Alternative facial detection models can be integrated with minimal refactoring.
- Output format is designed to be easily merged with eye-tracking experiment data.

## Example Usage

### Detect Facial Landmarks from Videos

```python
from detect_videos import process_all_videos

process_all_videos(
    video_dir="./videos",
    output_dir="./landmark_csvs",
    model_path="./shape_predictor_68_face_landmarks.dat",
    save_raw=False,
    save_marked=True
)
```

### Compare Fixations to Facial Regions (Video)

```python
from comparison_fixation_videos import process_fixation_videos

process_fixation_videos(
    fixation_path="./fixations.csv",
    csvtable_dir="./landmark_csvs",
    videofilter=".mp4",
    output_path="./fixation_results.csv"
)
```

### Generate Annotated Videos

```python
from facial_video_processor import process_videos

process_videos(
    video_dir="./videos",
    output_dir="./annotated_videos",
    model_path="./shape_predictor_68_face_landmarks.dat",
    max_workers=4
)
```

## Conclusion

This toolkit offers a practical and flexible solution for researchers and developers working on facial perception and eye-tracking analysis. Its modularity, efficiency, and extensibility make it well-suited for cognitive psychology, HCI, and behavioral neuroscience research contexts.

