# Skill: AprilTag Detection with pupil-apriltags

## Overview
`pupil-apriltags` is a Python wrapper for the official C AprilTag library. It is significantly faster than many other implementations.

## Usage Pattern
```python
from pupil_apriltags import Detector
import cv2

at_detector = Detector(
    families='tag36h11',
    nthreads=1,
    quad_decimate=1.0,
    quad_sigma=0.0,
    refine_edges=1,
    decode_sharpening=0.25,
    searchpath=['apriltags']
)

# In the loop:
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
results = at_detector.detect(gray, estimate_tag_pose=False, camera_params=None, tag_size=None)
```

## Pose Estimation Note
While `detect()` can estimate pose, it is often better to use OpenCV's `solvePnP` with calibrated intrinsic parameters for more control and accuracy.
