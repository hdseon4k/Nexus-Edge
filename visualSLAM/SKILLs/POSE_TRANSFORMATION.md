# Skill: World Coordinate System & Pose Transformation

## 1. Coordinate Convention
- **World Frame ($W$):** Arbitrary fixed point (e.g., first tag).
- **Camera Frame ($C$):** $Z$ forward, $X$ right, $Y$ down.
- **Tag Frame ($T$):** Usually $Z$ normal to tag surface.

## 2. Transformation Math
To find the camera pose in the world ($T_{wc}$):
$$T_{wc} = T_{wt} \times T_{tc}$$
Where:
- $T_{wt}$ is the pre-registered pose of the tag in the world (from `map.yaml`).
- $T_{tc}$ is the pose of the camera relative to the tag (calculated via `solvePnP`).

## 3. solvePnP Usage
```python
# object_points: 3D corners of the tag in its own frame (meters)
# image_points: 2D corners detected by AprilTag
ret, rvec, tvec = cv2.solvePnP(object_points, image_points, K, D)
# Convert rvec to matrix
R, _ = cv2.Rodrigues(rvec)
# T_tc (Camera relative to Tag)
# Note: solvePnP returns Tag relative to Camera, so inversion might be needed depending on perspective.
```
