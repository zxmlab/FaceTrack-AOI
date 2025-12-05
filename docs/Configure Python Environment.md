# Configure Python Environment
It is recommended to use a virtual environment. Below is a demonstration of how to set one up:

1. Install Miniconda
2. Create a new virtual environment
```
conda create -n facetrack python
```
3. Activate the facetrack environment
```
conda activate facetrack
```
4. Install required packages
```
conda install numpy pandas tqdm
conda install -c conda-forge opencv dlib moviepy
conda install -c conda-forge kivy
conda install -c conda-forge ffpyplayer
```
5. Verify installation (run in Python shell)
```
import numpy, cv2, dlib, pandas, tqdm, moviepy, kivy, ffpyplayer
```

6. If installation fails, close and reopen the Miniconda terminal, then reconfigure using:
```
conda remove -n facetrack --all
conda create -n facetrack python=3.13 numpy pandas tqdm opencv dlib moviepy kivy -c conda-forge
conda activate facetrack
```
