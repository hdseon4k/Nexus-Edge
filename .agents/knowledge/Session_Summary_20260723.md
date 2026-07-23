# Session Summary: 2026-07-23 (Setup A - Edge Vision & UI Infrastructure)

## 1. Tactical HUD & UI Improvements (`src/static/control_ui.html`)
- **Theme**: Applied a Cybernetic / Tactical Engineering HUD design using `JetBrains Mono` and `Share Tech Mono` fonts, with Cyan/Amber accents.
- **Log Monitor**: Built a real-time log viewer container intercepting the backend stdout/stderr. Added `AUTO_SCROLL` toggle functionality.
- **Responsive Layout**: Replaced rigid `100vh` body lock with a `min-height` flow and customized the main browser scrollbar to match the HUD aesthetics.
- **Video Panel**: Embedded a live MJPEG stream panel (`/api/video_feed`). Limited max height to `35vh` to prevent oversized video on ultra-wide desktop monitors while keeping 100% width on vertical smartphones.
- **Calibration Overlay**: Added an animated, translucent Progress Bar overlay directly on top of the video stream that polls `/api/calibration/status`.
- **Pre-Flight Checklist (Hardware Preset)**: Implemented an expandable alert card detailing the ActionCam's required hardware preset: 1080p 60fps, 1/250s Shutter Speed, MF, and explicitly warning against AI Auto-Framing. 

## 2. Zero-Latency Camera Architecture (`src/app.py`)
- **Multi-Threaded Frame Grabber**: Introduced a dedicated thread solely for pulling frames from the MJPEG stream (`127.0.0.1:8081`). This completely bypasses the OpenCV buffer buildup issue, guaranteeing the analysis thread always pulls the absolute latest frame.
- **Performance Downscaling**: Before passing the frame to the heavy `cv2.findChessboardCorners` or `cv2.ORB_create()` functions, the frame is actively downscaled from 1920x1080 to 640x360. This reduced the pixel workload to ~11% (1/9th), solving the S24 Ultra's CPU throttling and ensuring snappy UI updates.
- **MJPEG Generator**: Created a generator thread that streams the latest frame (with ORB points and calibration UI drawn over it) back to the browser without re-resizing the already downscaled frame, saving additional CPU cycles.

## 3. Log Interception & System Diagnostics
- **LogInterceptor**: Rerouted `sys.stdout` and `sys.stderr` to capture Python print statements and exceptions.
- **OS-Level FD Redirection**: Re-opened file descriptor `2` (STDERR) via `os.dup2` to an anonymous pipe to capture low-level C++ errors originating from `libav` (FFmpeg) and `OpenCV`.
- **ANSI Stripping**: Implemented a regex filter to clean up raw terminal color codes before sending them via the HTTP JSON `/api/telemetry` endpoint.

## 4. Hardware Optimization Strategy (ADR)
- Drafted `production_hardware_roadmap.md` outlining the roadmap for transitioning from Termux (Python) to Android Native (C++/Kotlin).
- Detailed the role of **NPU** (NNAPI for YOLO/Deep Learning), **GPU** (OpenCL/Vulkan for pre-processing/downscaling), and **CPU** (NEON SIMD for SLAM coordinate math).

---
#Session #ADR #Knowledge #Phase1 #Camera #UI
[[README]] [[STATUS]]
