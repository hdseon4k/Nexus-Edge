# Research: Wireless Video Streaming for EOS M6 Mark II

## 1. Options for Wireless Acquisition

### A. EOS Webcam Utility Pro (Wi-Fi Support)
- **Method:** Newer versions of the EOS Webcam Utility (Pro version) support wireless connection over the local network.
- **Pros:** Integrated with existing `cv2.VideoCapture()` workflow.
- **Cons:** Paid subscription may be required for full features; latency can be higher than wired.

### B. Smartphone Bridge (Camera Connect App)
- **Method:** Camera -> Wi-Fi -> Smartphone -> RTSP/NDI -> PC.
- **Pros:** Standard Canon Wi-Fi usage.
- **Cons:** High latency, multiple conversion steps, unsuitable for high-speed SLAM.

### C. Wireless HDMI Transmitter
- **Method:** Camera HDMI Out -> Wireless Transmitter -> Receiver -> PC HDMI Capture Card.
- **Pros:** Lowest latency, best resolution (1080p), highly stable.
- **Cons:** Expensive hardware required.

### D. RTSP/NDI via Third-party Apps
- **Method:** If the camera supports clean HDMI, using an NDI encoder or a dedicated wireless capture device.

## 2. Recommended Path for SLAM
For SLAM, **Low Latency** and **Fixed Exposure/Focus** are critical.
1. **Wireless HDMI** is the professional choice for performance.
2. **EOS Webcam Utility Pro** (Wi-Fi mode) is the most accessible software solution.

## 3. Impact on SLAM
- **Latency:** Delays between movement and observation can cause tracking loss.
- **Compression:** High compression artifacts can interfere with AprilTag corner detection.
