"""
Automatic Camera Lens Calibration Manager
Captures calibration board frames (ChArUco / Chessboard), tracks progress %,
computes intrinsic K matrix and distortion coefficients D, and saves to config/camera_calibration.json.
"""

import os
import json
import time
import cv2
import numpy as np

class AutoCalibrationManager:
    def __init__(self, target_frames=20, config_path="config/camera_calibration.json"):
        self.target_frames = target_frames
        self.config_path = config_path
        
        self.active = False
        self.captured_frames = 0
        self.progress_percent = 0
        self.status_message = "Ready for calibration."
        self.instruction = "Press 'Start Auto Calibration' and present ChArUco / Chessboard to camera."
        self.rms_error = 0.0
        
        self.last_capture_time = 0
        self.capture_delay = 1.0  # 1 second delay between automatic captures
        
        # Board settings (ChArUco 7x10)
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_100)
        self.charuco_board = cv2.aruco.CharucoBoard((7, 10), 0.025, 0.0125, self.aruco_dict)
        self.detector_params = cv2.aruco.DetectorParameters()

        self.all_corners = []
        self.all_ids = []
        self.frame_size = (1920, 1080)
        self.frame_size = (1920, 1080)

    def start_calibration(self):
        """Starts new auto calibration session"""
        self.active = True
        self.captured_frames = 0
        self.progress_percent = 0
        self.all_corners = []
        self.all_ids = []
        self.last_capture_time = time.time()
        self.status_message = "COLLECTING_FRAMES"
        self.instruction = "Hold the calibration board in front of the camera and tilt slowly at various angles (0/20 frames)."

    def stop_calibration(self):
        """Stops calibration session"""
        self.active = False
        self.status_message = "CANCELLED"
        self.instruction = "Calibration process stopped."

    def process_frame(self, frame):
        """Processes input frame for calibration board detection and collects 3D-2D points"""
        if not self.active or frame is None:
            return frame

        self.frame_size = (frame.shape[1], frame.shape[0])
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        markerCorners, markerIds, rejected = cv2.aruco.detectMarkers(gray, self.aruco_dict, parameters=self.detector_params)
        
        found = False
        charuco_corners = None
        charuco_ids = None

        if markerIds is not None and len(markerIds) > 0:
            charuco_retval, charuco_corners, charuco_ids = cv2.aruco.interpolateCornersCharuco(markerCorners, markerIds, gray, self.charuco_board)
            if charuco_corners is not None and charuco_ids is not None and len(charuco_corners) > 4:
                found = True
        
        self.latest_found = found
        self.latest_corners = len(charuco_corners) if found else 0

        if found:
            current_time = time.time()
            if current_time - self.last_capture_time >= self.capture_delay:
                self.all_corners.append(charuco_corners)
                self.all_ids.append(charuco_ids)
                self.captured_frames += 1
                self.last_capture_time = current_time

                self.progress_percent = int((self.captured_frames / self.target_frames) * 100)
                self.instruction = f"Keep tilting board! Capturing frame {self.captured_frames}/{self.target_frames} ({self.progress_percent}%)."

                # Check if required frames collected
                if self.captured_frames >= self.target_frames:
                    self.compute_and_save_calibration()

            # Draw corners for feedback
            cv2.aruco.drawDetectedCornersCharuco(frame, charuco_corners, charuco_ids, (0, 0, 255))
            
            # Draw green outline around the detected pattern
            rect = cv2.minAreaRect(charuco_corners)
            box = cv2.boxPoints(rect)
            box = np.int32(box)
            cv2.drawContours(frame, [box], 0, (0, 255, 0), 4)

        return frame

    def compute_and_save_calibration(self):
        """Computes camera intrinsic matrix and distortion coefficients and saves JSON"""
        self.status_message = "COMPUTING"
        self.instruction = "Calculating lens distortion matrix..."

        try:
            ret, K, dist, rvecs, tvecs = cv2.aruco.calibrateCameraCharuco(
                self.all_corners, self.all_ids, self.charuco_board, self.frame_size, None, None
            )
        except Exception as e:
            # Fallback for newer OpenCV versions if calibrateCameraCharuco is deprecated
            obj_points = []
            img_points = []
            for corners, ids in zip(self.all_corners, self.all_ids):
                objP, imgP = self.charuco_board.matchImagePoints(corners, ids)
                obj_points.append(objP)
                img_points.append(imgP)
            ret, K, dist, rvecs, tvecs = cv2.calibrateCamera(
                obj_points, img_points, self.frame_size, None, None
            )

        self.rms_error = round(float(ret), 3)

        calib_data = {
            "description": "Auto-calibrated Camera Intrinsic Parameters and Distortion",
            "resolution": {
                "width": self.frame_size[0],
                "height": self.frame_size[1]
            },
            "K": K.tolist(),
            "dist_coeffs": dist.ravel().tolist(),
            "rms_reprojection_error": self.rms_error,
            "calibrated_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(calib_data, f, indent=2)

        self.active = False
        self.status_message = "COMPLETED"
        self.instruction = f"Calibration Finished! RMS Error: {self.rms_error}px (Ideal: <0.5px). Saved to config/camera_calibration.json."

    def get_status(self):
        """Returns JSON status for Web UI polling"""
        return {
            "active": self.active,
            "progress_percent": self.progress_percent,
            "captured_frames": self.captured_frames,
            "target_frames": self.target_frames,
            "status_message": self.status_message,
            "instruction": self.instruction,
            "rms_error": self.rms_error,
            "board_found": getattr(self, 'latest_found', False),
            "corners_detected": getattr(self, 'latest_corners', 0)
        }
