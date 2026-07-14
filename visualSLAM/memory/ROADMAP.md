# Visual SLAM Project Roadmap: AprilTag & EOS M6 Mark II

This document outlines the step-by-step procedure to complete the AprilTag-based Visual SLAM project.

## Phase 1: Preparation & Calibration
1.  **Tag Generation & Printing**
    *   **Family:** Use `tag36h11` for high robustness.
    *   **Tool:** Use online generators or the `apriltag` Python library to generate tags.
    *   **Printing:** Print tags on a flat, non-reflective surface. **Crucial:** Measure the exact physical size of the black square (e.g., 0.165 meters) for pose estimation accuracy.
2.  **Camera Calibration**
    *   Capture 20-30 images of a chessboard pattern using the EOS M6 Mark II.
    *   Run `src/calibrate.py` to generate `calibration.yaml`.
    *   Verify that `reprojection error` is low (< 0.5 pixels).

## Phase 2: Core Implementation
3.  **Tag Coordinate Registration (The Map)**
    *   Create a `map.yaml` file.
    *   Define the world coordinates $(x, y, z)$ of each tag's center and its orientation.
    *   Example: Tag ID 0 is at $(0, 0, 0)$, Tag ID 1 is at $(1.0, 0, 0)$.
4.  **AprilTag Detection & Pose Estimation**
    *   Implement `src/detect.py` using `pupil-apriltags`.
    *   Extract 2D corner coordinates from the image.
    *   Use `cv2.solvePnP` with camera intrinsics and physical tag size to calculate $R$ (rotation) and $t$ (translation) relative to the tag.
5.  **Coordinate Transformation (SLAM)**
    *   Convert Tag-to-Camera pose to Camera-to-World pose using the pre-registered map.
    *   $T_{world\_camera} = T_{world\_tag} \times T_{tag\_camera}$
    *   Handle multiple tags: If multiple tags are visible, average their estimated poses or use a Kalman Filter/Factor Graph for optimization.

## Phase 3: Visualization & Integration
6.  **Real-time Visualization**
    *   Project a 3D axis on each detected tag.
    *   Display the camera's current $(x, y, z)$ position on the screen.
7.  **Logging & Analysis**
    *   Save the estimated trajectory to a CSV or JSON file for post-analysis.

## Phase 4: Refinement
8.  **Filtering:** Implement a simple EKF (Extended Kalman Filter) to smooth the camera movement.
9.  **Mapping Mode:** Allow the system to "discover" new tags and add them to the map automatically based on current camera pose.

---
*Created on 2026-05-21. Track progress in memory/LOG.md.*
