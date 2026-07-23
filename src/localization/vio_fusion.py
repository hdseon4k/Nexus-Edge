"""
Visual-Inertial Odometry (VIO) Extended Kalman Filter (EKF) Fusion Module
Fuses visual AprilTag camera pose estimation with S24 Ultra IMU (accel/gyro) data.
"""

import time
import numpy as np

class VIOFusionEKF:
    def __init__(self):
        # State vector: [x, y, vx, vy]
        self.state = np.zeros((4, 1), dtype=np.float64)
        
        # State covariance P
        self.P = np.eye(4, dtype=np.float64) * 0.1
        
        # Process noise covariance Q
        self.Q = np.eye(4, dtype=np.float64) * 0.05
        
        # Measurement noise covariance R (Visual Pose)
        self.R = np.eye(2, dtype=np.float64) * 0.02
        
        self.last_update_time = time.time()

    def predict_imu(self, ax, ay, dt=None):
        """Predicts next state using IMU accelerations (ax, ay)"""
        current_time = time.time()
        if dt is None:
            dt = current_time - self.last_update_time
        self.last_update_time = current_time

        # State transition matrix F
        F = np.array([
            [1, 0, dt,  0],
            [0, 1,  0, dt],
            [0, 0,  1,  0],
            [0, 0,  0,  1]
        ], dtype=np.float64)

        # Control input matrix B (acceleration)
        B = np.array([
            [0.5 * dt**2, 0],
            [0, 0.5 * dt**2],
            [dt, 0],
            [0, dt]
        ], dtype=np.float64)

        u = np.array([[ax], [ay]], dtype=np.float64)

        # State prediction
        self.state = F @ self.state + B @ u
        self.P = F @ self.P @ F.T + self.Q

    def update_visual_pose(self, vision_x, vision_y):
        """Corrects state estimation using Visual AprilTag Pose (vision_x, vision_y)"""
        # Measurement matrix H (observes x and y)
        H = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0]
        ], dtype=np.float64)

        z = np.array([[vision_x], [vision_y]], dtype=np.float64)
        y = z - H @ self.state  # Innovation residual

        S = H @ self.P @ H.T + self.R  # Innovation covariance
        K = self.P @ H.T @ np.linalg.inv(S)  # Kalman Gain

        # Update state and covariance
        self.state = self.state + K @ y
        self.P = (np.eye(4) - K @ H) @ self.P

        return self.get_position()

    def get_position(self):
        """Returns current filtered 2D position (x, y)"""
        return {
            "x": round(float(self.state[0][0]), 3),
            "y": round(float(self.state[1][0]), 3),
            "vx": round(float(self.state[2][0]), 3),
            "vy": round(float(self.state[3][0]), 3)
        }

if __name__ == "__main__":
    ekf = VIOFusionEKF()
    print("Initial Position:", ekf.get_position())
    ekf.predict_imu(ax=0.1, ay=0.0, dt=0.5)
    print("After IMU Predict:", ekf.get_position())
    ekf.update_visual_pose(vision_x=0.1, vision_y=0.0)
    print("After Visual Update:", ekf.get_position())
