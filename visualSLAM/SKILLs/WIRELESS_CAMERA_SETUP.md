# Skill: Wireless Camera Setup for Visual SLAM

## Overview
Wireless streaming introduces latency and jitter. This skill focuses on minimizing these issues for AprilTag detection.

## Setup Procedure: EOS Webcam Utility Pro (Wi-Fi)
1. **Camera Side:** Enable Wi-Fi/NFC on EOS M6 Mark II. Select "Connect to Computer".
2. **PC Side:** Install **EOS Webcam Utility Pro**.
3. **Pairing:** Follow the pairing instructions in the utility.
4. **Accessing:** The camera will appear as a virtual webcam. Use `cv2.VideoCapture(1)` (or the specific index).

## Troubleshooting Latency
- **Dedicated Router:** Use a 5GHz Wi-Fi router dedicated to the camera and PC.
- **Lower Resolution:** If the stream lags, lower the resolution to 720p to reduce bandwidth.
- **Keyframe Interval:** If using RTSP, set the buffer size in OpenCV to 1 to avoid processing "old" frames:
  ```python
  cap = cv2.VideoCapture(url)
  cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
  ```
