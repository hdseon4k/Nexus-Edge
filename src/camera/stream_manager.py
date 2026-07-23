"""
Stream Manager Module for Setup A (Insta360 / S24 Ultra Camera Stream)
Handles frame capture, intrinsic camera matrix scaling, and lens distortion correction.
"""

import cv2
import numpy as np

class CameraStreamManager:
    def __init__(self, camera_id=0, width=1920, height=1080):
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.cap = None
        
        # Default Intrinsic Matrix K (To be updated via ChArUco Calibration)
        self.fx = 1150.0  # Focal length X
        self.fy = 1150.0  # Focal length Y
        self.cx = width / 2.0   # Optical center X
        self.cy = height / 2.0  # Optical center Y
        
        self.K = np.array([
            [self.fx, 0, self.cx],
            [0, self.fy, self.cy],
            [0, 0, 1]
        ], dtype=np.float64)
        
        # Lens distortion coefficients (k1, k2, p1, p2, k3)
        self.dist_coeffs = np.zeros((5, 1), dtype=np.float64)

    def initialize(self):
        """Initializes OpenCV Video Capture"""
        import os
        cam_src = os.environ.get("CAMERA_SOURCE", "http://127.0.0.1:8080/video")
        if cam_src.isdigit():
            cam_src = int(cam_src)
            
        self.cap = cv2.VideoCapture(cam_src)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        return self.cap.isOpened()

    def set_calibration(self, K, dist_coeffs):
        """Sets calibrated intrinsic matrix and distortion coefficients"""
        self.K = np.array(K, dtype=np.float64)
        self.dist_coeffs = np.array(dist_coeffs, dtype=np.float64)

    def read_frame(self, undistort=True):
        """Reads frame and optionally applies lens undistortion"""
        if self.cap is None or not self.cap.isOpened():
            return False, None
            
        ret, frame = self.cap.read()
        if not ret or frame is None:
            return False, None
            
        if undistort:
            frame = cv2.undistort(frame, self.K, self.dist_coeffs)
            
        return True, frame

    def release(self):
        """Releases camera resource"""
        if self.cap and self.cap.isOpened():
            self.cap.release()
            
if __name__ == "__main__":
    stream = CameraStreamManager()
    print("Camera Stream Manager Initialized. K Matrix:")
    print(stream.K)
