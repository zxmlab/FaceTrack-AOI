### Image Experiment
```python
# Step 1: Detect Facial Landmarks

from detect_images import process_images

process_images(
    image_dir = "./example_data/Images",
    output_dir = "./example_data/Images/output",
    model_path = "./model/shape_predictor_68_face_landmarks.dat",
    save_marked = True
)

# Step 2: Compare Fixations to Facial Regions

from comparision_fixation_images import process_fixation_image

process_fixation_image(
    input_path = "./example_data/fixation_data/fixation_data_image.txt",
    csvtable_path = "./example_data/Images/output/landmarks.csv",
    image_column = "Image_Column",
    fix_x_column = "CURRENT_FIX_X",
    fix_y_column = "CURRENT_FIX_Y",
    output_path = "./example_data/fixation_data/output/fixation_data_image_out.csv",
)
```

### Video Experiment
```python
# Step 1: Detect Facial Landmarks

from detect_videos import process_all_videos

process_all_videos(
    video_dir = "./example_data/videos",
    output_dir = "./example_data/videos/output",
    model_path = "./model/shape_predictor_68_face_landmarks.dat",
    save_raw = True,
    save_marked = True,
    video_filter = ".mp4",
    max_workers = 8
)

# Step 2: Compare Fixations to Facial Regions

from comparision_fixation_videos import process_fixation_video

process_fixation_video(
    input_path = "./example_data/fixation_data/fixation_data_video.txt",
    csvtable_dir = "./example_data/videos/output",
    fix_x_column = "CURRENT_FIX_X",
    fix_y_column = "CURRENT_FIX_Y",
    video_name_column = "VIDEO_NAME_END",
    frame_index_column = "VIDEO_FRAME_INDEX_END",
    video_filter = ".mp4",
    output_path = "./example_data/fixation_data/output/fixation_data_video_out.csv"
)

```

#### Generate Annotated Videos
```python
from facial_video_processor import process_videos

process_videos(
    video_dir = "./example_data/videos",
    output_dir = "./example_data/videos/output",
    model_path = "./model/shape_predictor_68_face_landmarks.dat",
    max_workers = 8
)
```
