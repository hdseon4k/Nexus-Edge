# Research: AprilTag SLAM Components

## 1. AprilTag Detection Libraries
- **pupil-apriltags:** (Recommended) Very fast, supports latest tag families (Tag36h11, etc.). Good Windows support via wheels.
- **opencv-contrib-python (aruco/apriltag):** Built-in, but often slower and less robust than the official C implementation.
- **dt-apriltags:** Another Python wrapper, common in robotics.

## 2. Camera Interfacing (EOS M6 Mark II)
- **HDMI Capture Card:** Standard `cv2.VideoCapture(0)`. Best for low latency.
- **EOS Webcam Utility:** Virtual webcam via USB. `cv2.VideoCapture(1)`.
- **gPhoto2 / libgphoto2:** High resolution but high latency. Not ideal for real-time SLAM.

## 3. Calibration
- Must use a checkerboard or ArUco board to find `fx, fy, cx, cy` and distortion coefficients `k1, k2, p1, p2`.

## Recommendation
1. Install `opencv-python` and `pupil-apriltags`.
2. Perform intrinsic calibration.
3. Use `solvePnP` for pose estimation from detected tag corners.
