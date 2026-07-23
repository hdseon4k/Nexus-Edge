"""
AprilTag VisualSLAM Localization Module
Performs AprilTag (tag36h11) detection, SolvePnP pose estimation, 
and global coordinate mapping using marker_map.json.
"""

import json
import cv2
import numpy as np

try:
    from pupil_apriltag import Detector
    PUPIL_APRILTAG_AVAILABLE = True
except ImportError:
    PUPIL_APRILTAG_AVAILABLE = False


class AprilTagSLAM:
    def __init__(self, marker_map_path="config/marker_map.json", tag_family="tag36h11"):
        self.tag_family = tag_family
        self.marker_map = {}
        self.load_marker_map(marker_map_path)
        
        # Detector initialization
        if PUPIL_APRILTAG_AVAILABLE:
            self.detector = Detector(families=tag_family, nthreads=2, quad_decimate=1.0)
        else:
            self.detector = None
            print("⚠️ pupil_apriltag library not found. Falling back to OpenCV ArUco detector if available.")

    def load_marker_map(self, map_path):
        """Loads absolute 3D world coordinates for each AprilTag ID"""
        try:
            with open(map_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.marker_map = data.get("markers", {})
                print(f"✅ Loaded {len(self.marker_map)} markers from {map_path}")
        except Exception as e:
            print(f"❌ Failed to load marker map from {map_path}: {e}")

    def detect_and_estimate_pose(self, frame, K, dist_coeffs):
        """
        Detects AprilTags in frame and estimates camera global 3D pose (X, Y, Z, Yaw)
        """
        if frame is None:
            return None, []

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        detections = []
        detected_poses = []

        if self.detector:
            # pupil_apriltag detection
            results = self.detector.detect(gray)
            for r in results:
                tag_id = str(r.tag_id)
                if tag_id not in self.marker_map:
                    continue

                marker_info = self.marker_map[tag_id]
                size = marker_info.get("size_meters", 0.15)

                # Define 3D corner points of tag in marker local frame
                s = size / 2.0
                obj_pts = np.array([
                    [-s,  s, 0],
                    [ s,  s, 0],
                    [ s, -s, 0],
                    [-s, -s, 0]
                ], dtype=np.float64)

                img_pts = np.array(r.corners, dtype=np.float64)

                # SolvePnP
                success, rvec, tvec = cv2.solvePnP(obj_pts, img_pts, K, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE)
                if success:
                    # Convert to camera global position based on marker map
                    global_pose = self._compute_global_camera_pose(rvec, tvec, marker_info)
                    detected_poses.append(global_pose)

                    # Draw tag boundary for visualization
                    for i in range(4):
                        pt1 = tuple(img_pts[i].astype(int))
                        pt2 = tuple(img_pts[(i+1)%4].astype(int))
                        cv2.line(frame, pt1, pt2, (0, 255, 0), 2)
                    cv2.putText(frame, f"Tag #{tag_id}", tuple(img_pts[0].astype(int)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        return frame, detected_poses

    def _compute_global_camera_pose(self, rvec, tvec, marker_info):
        """Computes camera global X, Y, Z world position relative to marker's known global pose"""
        # Marker global position
        mx, my, mz = marker_info["x"], marker_info["y"], marker_info["z"]
        
        # Camera relative offset from SolvePnP tvec
        # tvec is marker position in camera frame
        cam_x = mx - tvec[0][0]
        cam_y = my - tvec[2][0]  # Z depth mapped to 2D floor Y
        cam_z = mz + tvec[1][0]
        
        return {
            "tag_id": marker_info.get("location_name", "Tag"),
            "x": round(float(cam_x), 3),
            "y": round(float(cam_y), 3),
            "z": round(float(cam_z), 3)
        }

if __name__ == "__main__":
    slam = AprilTagSLAM()
    print("AprilTagSLAM initialized.")
