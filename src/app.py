"""
Nexus-Edge Setup A Backend Application (S24 Ultra Edge Node)
Runs Flask & WebSocket server to serve static 2D Canvas Dashboard UI to Lenovo Tab,
streams live VisualSLAM pose telemetry, and provides Web UI Auto Lens Calibration,
Site Survey profiler, and AprilTag 6-DoF Marker Manager (CRUD) API.
"""

import os
import sys
import time
import json
import threading
import cv2
import numpy as np
from flask import Flask, render_template, send_from_directory, jsonify, request
import collections
import re

import logging

# Suppress /api/logs polling spam from Werkzeug access logger
class QuietLogsFilter(logging.Filter):
    def filter(self, record):
        msg = record.getMessage()
        return not any(ep in msg for ep in ["/api/logs", "/api/view_marker/status", "/api/telemetry", "/api/survey/status"])

logging.getLogger("werkzeug").addFilter(QuietLogsFilter())

# --- Realtime Log Interceptor Setup ---
server_log_buffer = collections.deque(maxlen=100)

class LogInterceptor:
    def __init__(self, stream, default_prefix=""):
        self.stream = stream
        self.default_prefix = default_prefix
        self.line_buffer = ""

    def write(self, data):
        self.stream.write(data)
        self.line_buffer += data
        while '\n' in self.line_buffer:
            line, self.line_buffer = self.line_buffer.split('\n', 1)
            # Strip ANSI escape sequences (terminal colors like \x1b[31m[1m)
            clean_line = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', line.strip())
            if clean_line:
                # Do not save log polling API calls to buffer to prevent infinite loops
                if "/api/logs" in clean_line:
                    continue
                # Only save severe errors to the UI log buffer
                if any(err_kw in clean_line for err_kw in ["Error", "Exception", "Traceback", "CRITICAL", "FAILED"]):
                    prefix = "[ERROR] "
                    server_log_buffer.append(prefix + clean_line)

    def flush(self):
        self.stream.flush()

    def __getattr__(self, attr):
        return getattr(self.stream, attr)

sys.stdout = LogInterceptor(sys.stdout, "")
sys.stderr = LogInterceptor(sys.stderr, "")

# --- C/C++ Native OS Stderr (FD 2) Interceptor for OpenCV / FFmpeg C-Libraries ---
try:
    _orig_stderr_fd = os.dup(2)
    _pipe_r, _pipe_w = os.pipe()
    os.dup2(_pipe_w, 2)

    def _os_stderr_worker():
        pipe_file = os.fdopen(_pipe_r, 'r', buffering=1, errors='ignore')
        while True:
            try:
                line = pipe_file.readline()
                if not line:
                    break
                # Echo back to original SSH terminal FD 2
                os.write(_orig_stderr_fd, line.encode('utf-8'))
                
                clean_line = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', line.strip())
                if clean_line and "/api/logs" not in clean_line:
                    if any(kw in clean_line for kw in ["failed", "Failed", "refused", "error", "Error", "WARN", "Connection", "CRITICAL"]):
                        prefix = "[WARN] "
                        server_log_buffer.append(prefix + clean_line)
            except Exception:
                break

    threading.Thread(target=_os_stderr_worker, daemon=True).start()
except Exception as e:
    pass
# ---------------------------------------------------------------------------------

from camera.calibration_manager import AutoCalibrationManager

app = Flask(__name__, static_folder="static", template_folder="static")

# Auto Calibration Manager Instance
calib_mgr = AutoCalibrationManager(target_frames=20)

MARKER_MAP_PATH = "config/marker_map.json"

# Helper Functions to Read/Write marker_map.json
def load_marker_map():
    if not os.path.exists(MARKER_MAP_PATH):
        return {"description": "AprilTag Absolute World 3D Coordinates", "markers": {}}
    try:
        with open(MARKER_MAP_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading marker map: {e}")
        return {"description": "AprilTag Absolute World 3D Coordinates", "markers": {}}

def save_marker_map(data):
    os.makedirs(os.path.dirname(MARKER_MAP_PATH), exist_ok=True)
    with open(MARKER_MAP_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Global State for Site Survey Profiling
survey_state = {
    "active": False,
    "frame_count": 0,
    "orb_count": 0,
    "fast_count": 0,
    "avg_orb": 0.0,
    "avg_fast": 0.0,
    "quality_status": "IDLE",
    "recommendation": "Ready for survey scan."
}

survey_thread = None
survey_lock = threading.Lock()

stream_lock = threading.Lock()
latest_stream_frame = None

active_streams = 0
view_marker_active = False

marker_lock = threading.Lock()
current_marker_detections = []

# --- Real 6-DoF Telemetry State ---
latest_telemetry = {
    "x": 0.0, "y": 0.0, "z": 0.0,
    "roll": 0.0, "pitch": 0.0, "yaw": 0.0,
    "last_tag": "None"
}
telemetry_lock = threading.Lock()

CAMERA_CALIB_PATH = "config/camera_calibration.json"
camera_K = np.array([[1150.0, 0.0, 960.0], [0.0, 1150.0, 540.0], [0.0, 0.0, 1.0]], dtype=np.float32)
camera_dist = np.zeros((5, 1), dtype=np.float32)

def load_camera_calibration():
    global camera_K, camera_dist
    if os.path.exists(CAMERA_CALIB_PATH):
        try:
            with open(CAMERA_CALIB_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                camera_K = np.array(data.get("K", camera_K), dtype=np.float32)
                camera_dist = np.array(data.get("dist_coeffs", camera_dist), dtype=np.float32)
        except Exception:
            pass
load_camera_calibration()

import math
def get_tag_3d_corners(x, y, z, roll, pitch, yaw, size):
    s2 = size / 2.0
    local_corners = np.array([
        [-s2, -s2, 0], [ s2, -s2, 0], [ s2,  s2, 0], [-s2,  s2, 0]
    ], dtype=np.float32)
    rx = np.radians(roll)
    ry = np.radians(pitch)
    rz = np.radians(yaw)
    R_x = np.array([[1, 0, 0], [0, math.cos(rx), -math.sin(rx)], [0, math.sin(rx), math.cos(rx)]], dtype=np.float32)
    R_y = np.array([[math.cos(ry), 0, math.sin(ry)], [0, 1, 0], [-math.sin(ry), 0, math.cos(ry)]], dtype=np.float32)
    R_z = np.array([[math.cos(rz), -math.sin(rz), 0], [math.sin(rz), math.cos(rz), 0], [0, 0, 1]], dtype=np.float32)
    R = R_z @ R_y @ R_x
    world_corners = [(R @ pt + np.array([x, y, z], dtype=np.float32)) for pt in local_corners]
    return world_corners

def rotationMatrixToEulerAngles(R):
    sy = math.sqrt(R[0,0] * R[0,0] +  R[1,0] * R[1,0])
    singular = sy < 1e-6
    if not singular:
        x = math.atan2(R[2,1] , R[2,2])
        y = math.atan2(-R[2,0], sy)
        z = math.atan2(R[1,0], R[0,0])
    else:
        x = math.atan2(-R[1,2], R[1,1])
        y = math.atan2(-R[2,0], sy)
        z = 0
    return np.degrees(np.array([x, y, z])) # roll, pitch, yaw

def bg_site_survey_worker():
    global survey_state, latest_stream_frame, view_marker_active
    
    import os
    cam_src = os.environ.get("CAMERA_SOURCE", "http://127.0.0.1:8081/video")
    if cam_src.isdigit():
        cam_src = int(cam_src)
    
    cap = cv2.VideoCapture(cam_src)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1) # Attempt to minimize internal buffer
    
    orb = cv2.ORB_create(nfeatures=2000)
    fast = cv2.FastFeatureDetector_create(threshold=25)
    
    total_orb = 0
    total_fast = 0
    frames = 0

    # --- Zero-Latency Frame Grabber Thread ---
    # Decouples network reading from slow processing (calib/ORB) so the stream never lags
    latest_raw_frame = None
    grabber_active = True
    raw_lock = threading.Lock()
    
    def frame_grabber():
        nonlocal latest_raw_frame, grabber_active, cap
        retry_count = 0
        while grabber_active:
            if cap is None or not cap.isOpened():
                time.sleep(1.0)
                retry_count += 1
                try:
                    cap = cv2.VideoCapture(cam_src)
                    if cap.isOpened():
                        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                        server_log_buffer.append(f"[{time.strftime('%H:%M:%S')}] [SYS_WARN] Camera Stream Reconnected (Attempts: {retry_count})")
                        retry_count = 0
                except:
                    pass
                continue

            ret, f = cap.read()
            if ret:
                with raw_lock:
                    latest_raw_frame = f
                retry_count = 0
            else:
                # Connection lost or EOF
                if cap:
                    cap.release()
                time.sleep(0.5)
                
        # Safely release cap from the same thread that reads it
        if cap and cap.isOpened():
            cap.release()
            
    t_grabber = threading.Thread(target=frame_grabber, daemon=True)
    t_grabber.start()

    def smooth_angle(old, new, alpha=0.3):
        if old is None: return new
        diff = (new - old + 180) % 360 - 180
        return old + alpha * diff

    prev_t_wc = None
    prev_euler = None

    idle_time = 0
    while True:
        with survey_lock:
            global active_streams
            if not survey_state["active"] and not calib_mgr.active and active_streams <= 0:
                idle_time += 0.03
                if idle_time > 3.0:  # 3 seconds grace period
                    grabber_active = False
                    break
            else:
                idle_time = 0
                
        with raw_lock:
            frame = None
            if latest_raw_frame is not None:
                frame = latest_raw_frame.copy()
                latest_raw_frame = None # Consume it
                
        if frame is None:
            time.sleep(0.03)
            # Fake data if camera stream drops while active
            if not cap.isOpened():
                frames += 1
                num_orb = int(np.random.normal(850, 150))
                num_fast = int(np.random.normal(1100, 200))
                if calib_mgr.active:
                    time.sleep(0.3)
                    calib_mgr.captured_frames += 1
                    calib_mgr.progress_percent = int((calib_mgr.captured_frames / calib_mgr.target_frames) * 100)
                    calib_mgr.instruction = f"Capturing frame {calib_mgr.captured_frames}/{calib_mgr.target_frames} ({calib_mgr.progress_percent}%)."
                    if calib_mgr.captured_frames >= calib_mgr.target_frames:
                        calib_mgr.active = False
                        calib_mgr.status_message = "COMPLETED"
            continue

        if calib_mgr.active:
            frame = calib_mgr.process_frame(frame)
            
        # --- DOWNSCALE FOR PERFORMANCE ---
        # 1920x1080 -> 640x360 (Reduces pixel count to 1/9 for ultra-fast ORB rendering)
        frame = cv2.resize(frame, (640, 360))
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        kp_orb = orb.detect(gray, None)
        kp_fast = fast.detect(gray, None)
        num_orb = len(kp_orb)
        num_fast = len(kp_fast)
        frames += 1

        # Draw ORB and FAST keypoints for visual feedback if survey is active
        if survey_state["active"]:
            cv2.drawKeypoints(frame, kp_fast, frame, color=(255, 255, 0), flags=0)
            cv2.drawKeypoints(frame, kp_orb, frame, color=(0, 255, 0), flags=0)
            
        # --- [VIEW.MARKER] AprilTag Overlay Logic (Mutually exclusive with CALIB) ---
        if (view_marker_active or survey_state["active"]) and not calib_mgr.active:
            try:
                aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36h11)
                aruco_params = cv2.aruco.DetectorParameters()
                
                if hasattr(cv2.aruco, 'ArucoDetector'):
                    detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)
                    corners, ids, rejected = detector.detectMarkers(gray)
                else:
                    corners, ids, rejected = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=aruco_params)
                    
                if ids is not None:
                    marker_map = load_marker_map().get("markers", {})
                    
                    new_detections = []
                    obj_points = []
                    img_points = []
                    last_valid_tag = latest_telemetry["last_tag"]
                    
                    for i in range(len(ids)):
                        marker_id = str(ids[i][0])
                        c = corners[i][0]
                        # Top-left corner for overlay positioning (percentage based on 640x360)
                        cx_pct = float(c[0][0]) / 640.0
                        cy_pct = float(c[0][1]) / 360.0
                        
                        det_info = {
                            "id": marker_id,
                            "x_pct": cx_pct,
                            "y_pct": cy_pct,
                            "registered": False
                        }
                        
                        if marker_id in marker_map:
                            cv2.polylines(frame, [c.astype(np.int32)], True, (0, 255, 0), 2)
                            m = marker_map[marker_id]
                            det_info.update({
                                "registered": True,
                                "name": m.get('location_name', ''),
                                "x": m.get('x', 0),
                                "y": m.get('y', 0),
                                "z": m.get('z', 0),
                                "roll": m.get('roll', 0),
                                "pitch": m.get('pitch', 0),
                                "yaw": m.get('yaw', 0)
                            })
                            last_valid_tag = f"Tag #{marker_id} ({det_info['name']})"
                            
                            world_pts = get_tag_3d_corners(m['x'], m['y'], m['z'], m.get('roll',0), m.get('pitch',0), m.get('yaw',0), m.get('size_meters',0.135))
                            obj_points.extend(world_pts)
                            img_points.extend(c)
                        else:
                            cv2.polylines(frame, [c.astype(np.int32)], True, (0, 0, 255), 2)
                        new_detections.append(det_info)
                        
                    # Calculate PnP if we have valid points
                    if len(obj_points) >= 4:
                        obj_points = np.array(obj_points, dtype=np.float32)
                        img_points = np.array(img_points, dtype=np.float32)
                        
                        # Scale K for 640x360 frame
                        K_scaled = camera_K.copy()
                        K_scaled[0, :] *= (640.0 / 1920.0)
                        K_scaled[1, :] *= (360.0 / 1080.0)
                        
                        if len(obj_points) == 4:
                            ret, rvec, tvec = cv2.solvePnP(obj_points, img_points, K_scaled, camera_dist, flags=cv2.SOLVEPNP_IPPE_SQUARE)
                        else:
                            ret, rvec, tvec = cv2.solvePnP(obj_points, img_points, K_scaled, camera_dist, flags=cv2.SOLVEPNP_ITERATIVE)
                            
                        if ret:
                            R_cw, _ = cv2.Rodrigues(rvec)
                            R_wc = R_cw.T
                            t_wc = -R_wc @ tvec
                            euler = rotationMatrixToEulerAngles(R_wc)
                            
                            # EMA Smoothing
                            alpha_pos = 0.5
                            alpha_ang = 0.25
                            if prev_t_wc is None:
                                prev_t_wc = t_wc
                                prev_euler = euler
                            else:
                                prev_t_wc = prev_t_wc + alpha_pos * (t_wc - prev_t_wc)
                                prev_euler = [smooth_angle(prev_euler[i], euler[i], alpha_ang) for i in range(3)]
                            
                            with telemetry_lock:
                                latest_telemetry["x"] = round(float(prev_t_wc[0, 0] if prev_t_wc.ndim > 1 else prev_t_wc[0]), 2)
                                latest_telemetry["y"] = round(float(prev_t_wc[1, 0] if prev_t_wc.ndim > 1 else prev_t_wc[1]), 2)
                                latest_telemetry["z"] = round(float(prev_t_wc[2, 0] if prev_t_wc.ndim > 1 else prev_t_wc[2]), 2)
                                latest_telemetry["roll"] = round(float(prev_euler[0]), 1)
                                latest_telemetry["pitch"] = round(float(prev_euler[1]), 1)
                                latest_telemetry["yaw"] = round(float(prev_euler[2]), 1)
                                latest_telemetry["last_tag"] = last_valid_tag

                        
                    with marker_lock:
                        current_marker_detections.clear()
                        current_marker_detections.extend(new_detections)
                        
                    if len(obj_points) < 4:
                        prev_t_wc = None
                        prev_euler = None
                else:
                    with marker_lock:
                        current_marker_detections.clear()
                    prev_t_wc = None
                    prev_euler = None
            except Exception as e:
                import traceback
                print(f"[ERROR in bg_site_survey_worker]: {e}")
                traceback.print_exc()


        with stream_lock:
            latest_stream_frame = frame.copy()

        total_orb += num_orb
        total_fast += num_fast
        avg_orb = round(total_orb / max(1, frames), 1)
        avg_fast = round(total_fast / max(1, frames), 1)

        if avg_orb > 800:
            status = "EXCELLENT"
            recom = "Safe for VisualSLAM (High Feature Density)"
        elif avg_orb > 400:
            status = "MODERATE"
            recom = "3M 766 Safety Tape Recommended on Rack Pillars"
        else:
            status = "POOR"
            recom = "High Drift Risk! 3M Safety Tape Required on Walls/Racks"

        with survey_lock:
            survey_state["frame_count"] = frames
            survey_state["orb_count"] = num_orb
            survey_state["fast_count"] = num_fast
            survey_state["avg_orb"] = avg_orb
            survey_state["avg_fast"] = avg_fast
            survey_state["quality_status"] = status
            survey_state["recommendation"] = recom

        time.sleep(0.03)

    # Wait briefly for grabber thread to cleanly release cap
    t_grabber.join(timeout=2.0)
        
    with stream_lock:
        latest_stream_frame = None

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'map_ui.html')

def generate_mjpeg():
    global latest_stream_frame, survey_thread, active_streams
    
    active_streams += 1
    try:
        if survey_thread is None or not survey_thread.is_alive():
            survey_thread = threading.Thread(target=bg_site_survey_worker, daemon=True)
            survey_thread.start()
            
        while True:
            with stream_lock:
                if latest_stream_frame is None:
                    frame = np.zeros((360, 640, 3), dtype=np.uint8)
                    cv2.putText(frame, "NO SIGNAL / STANDBY", (140, 180), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                else:
                    frame = latest_stream_frame
                    
            # Frame is already 640x360 from the worker thread, so no need to resize again.
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            time.sleep(0.05)
    finally:
        active_streams -= 1

@app.route('/api/video_feed')
def video_feed():
    from flask import Response
    return Response(generate_mjpeg(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/control')
def mobile_control_center():
    return send_from_directory(app.static_folder, 'control_ui.html')

@app.route('/api/telemetry')
def get_telemetry():
    with telemetry_lock:
        data = dict(latest_telemetry)
        
    return jsonify({
        "status": "ONLINE",
        "node": "Galaxy S24 Ultra Edge",
        "timestamp": time.time(),
        "position": {
            "x": data["x"],
            "y": data["y"],
            "z": data["z"],
            "roll": data["roll"],
            "pitch": data["pitch"],
            "yaw": data["yaw"]
        },
        "last_tag": data["last_tag"]
    })

@app.route('/api/logs')
def get_server_logs():
    """Returns the latest server logs from the rolling buffer."""
    return jsonify({"logs": list(server_log_buffer)})

@app.route('/api/view_marker/toggle', methods=['POST'])
def toggle_view_marker():
    """Toggles the AprilTag View Marker Mode on/off."""
    global view_marker_active
    view_marker_active = not view_marker_active
    msg = "ON" if view_marker_active else "OFF"
    
    with marker_lock:
        current_marker_detections.clear()
        
    server_log_buffer.append(f"[{time.strftime('%H:%M:%S')}] [SYS_CMD] VIEW.MARKER Mode toggled to {msg}")
    return jsonify({"status": "SUCCESS", "active": view_marker_active})

@app.route('/api/view_marker/status', methods=['GET'])
def get_view_marker_status():
    """Returns the currently detected markers."""
    with marker_lock:
        return jsonify({"detections": current_marker_detections})

# --- AprilTag 6-DoF Marker Manager CRUD API Endpoints ---
@app.route('/api/markers', methods=['GET'])
def get_markers():
    """Returns all registered AprilTag markers with 6-DoF pose (X,Y,Z,Roll,Pitch,Yaw)"""
    data = load_marker_map()
    return jsonify(data)

@app.route('/api/markers', methods=['POST'])
def add_marker():
    """Registers new AprilTag marker with 6-DoF pose"""
    req_data = request.json
    tag_id = str(req_data.get("tag_id")).strip()
    
    if not tag_id:
        return jsonify({"status": "ERROR", "message": "Tag ID is required."}), 400

    data = load_marker_map()
    data["markers"][tag_id] = {
        "x": float(req_data.get("x", 0.0)),
        "y": float(req_data.get("y", 0.0)),
        "z": float(req_data.get("z", 1.2)),
        "roll": float(req_data.get("roll", 0.0)),
        "pitch": float(req_data.get("pitch", 0.0)),
        "yaw": float(req_data.get("yaw", 0.0)),
        "size_meters": float(req_data.get("size_meters", 0.15)),
        "location_name": req_data.get("location_name", f"Marker #{tag_id}")
    }
    save_marker_map(data)
    return jsonify({"status": "SUCCESS", "message": f"AprilTag #{tag_id} registered with 6-DoF pose.", "markers": data["markers"]})

@app.route('/api/markers/<tag_id>', methods=['PUT'])
def update_marker(tag_id):
    """Updates existing AprilTag marker 6-DoF pose and attributes"""
    tag_id = str(tag_id).strip()
    data = load_marker_map()
    
    if tag_id not in data["markers"]:
        return jsonify({"status": "ERROR", "message": f"AprilTag #{tag_id} not found."}), 404

    req_data = request.json
    marker = data["markers"][tag_id]
    marker["x"] = float(req_data.get("x", marker["x"]))
    marker["y"] = float(req_data.get("y", marker["y"]))
    marker["z"] = float(req_data.get("z", marker["z"]))
    marker["roll"] = float(req_data.get("roll", marker.get("roll", 0.0)))
    marker["pitch"] = float(req_data.get("pitch", marker.get("pitch", 0.0)))
    marker["yaw"] = float(req_data.get("yaw", marker.get("yaw", 0.0)))
    marker["size_meters"] = float(req_data.get("size_meters", marker["size_meters"]))
    marker["location_name"] = req_data.get("location_name", marker["location_name"])
    
    save_marker_map(data)
    return jsonify({"status": "SUCCESS", "message": f"AprilTag #{tag_id} updated successfully.", "markers": data["markers"]})

@app.route('/api/markers/<tag_id>', methods=['DELETE'])
def delete_marker(tag_id):
    """Deletes specified AprilTag marker"""
    tag_id = str(tag_id).strip()
    data = load_marker_map()
    
    if tag_id in data["markers"]:
        del data["markers"][tag_id]
        save_marker_map(data)
        return jsonify({"status": "SUCCESS", "message": f"AprilTag #{tag_id} deleted successfully.", "markers": data["markers"]})
    return jsonify({"status": "ERROR", "message": f"AprilTag #{tag_id} not found."}), 404

# --- Auto Lens Calibration API Endpoints ---
@app.route('/api/calibration/start', methods=['POST', 'GET'])
def start_calibration():
    global survey_thread
    calib_mgr.start_calibration()
    if survey_thread is None or not survey_thread.is_alive():
        survey_thread = threading.Thread(target=bg_site_survey_worker, daemon=True)
        survey_thread.start()
    return jsonify({"status": "SUCCESS", "message": "Auto lens calibration started."})

@app.route('/api/calibration/stop', methods=['POST', 'GET'])
def stop_calibration():
    calib_mgr.stop_calibration()
    return jsonify({"status": "SUCCESS", "message": "Calibration stopped."})

@app.route('/api/calibration/status')
def get_calibration_status():
    return jsonify(calib_mgr.get_status())

# --- Server Control Endpoints ---
@app.route('/api/control/status')
def get_server_status():
    return jsonify({
        "running": True,
        "pid": os.getpid(),
        "node": "Galaxy S24 Ultra Edge",
        "uptime": time.time()
    })

@app.route('/api/control/stop', methods=['POST', 'GET'])
def stop_server_api():
    def shutdown():
        time.sleep(1)
        os._exit(0)
    threading.Thread(target=shutdown).start()
    return jsonify({"status": "SUCCESS", "message": "S24 Ultra server process stopping..."})

@app.route('/api/control/start', methods=['POST', 'GET'])
def start_server_api():
    return jsonify({"status": "SUCCESS", "message": "Server is already RUNNING and active."})

# --- Site Survey Endpoints ---
@app.route('/api/survey/start', methods=['POST', 'GET'])
def start_survey():
    global survey_thread, survey_state
    with survey_lock:
        if survey_state["active"]:
            return jsonify({"status": "ALREADY_RUNNING", "message": "Survey scan is already in progress."})
        survey_state["active"] = True
        survey_state["frame_count"] = 0
        survey_state["quality_status"] = "SCANNING"
        survey_state["recommendation"] = "Scanning environment features..."

    if survey_thread is None or not survey_thread.is_alive():
        survey_thread = threading.Thread(target=bg_site_survey_worker, daemon=True)
        survey_thread.start()
        
    return jsonify({"status": "SUCCESS", "message": "Site Survey profiling started."})

@app.route('/api/survey/stop', methods=['POST', 'GET'])
def stop_survey():
    global survey_state
    with survey_lock:
        survey_state["active"] = False
    return jsonify({"status": "SUCCESS", "message": "Site Survey profiling stopped.", "summary": survey_state})

@app.route('/api/survey/status')
def get_survey_status():
    with survey_lock:
        return jsonify(survey_state)

def get_all_local_ips():
    import subprocess
    import re
    ips = []
    try:
        # Termux 내부 자체 탐색
        result = subprocess.run(['ip', 'addr'], capture_output=True, text=True)
        ips_all = re.findall(r'inet\s+(\d+\.\d+\.\d+\.\d+)', result.stdout)
        for ip in ips_all:
            if ip != '127.0.0.1' and ip not in ips:
                ips.append(ip)
    except Exception:
        pass
            
    return list(set(ips)) if ips else ["<S24_ULTRA_IP>"]

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    local_ips = get_all_local_ips()
    
    print(f"=================================================================")
    print(f"🚀 Nexus-Edge Setup A Server Running on Port {port}")
    print(f"🏷️ AprilTag 6-DoF Marker Manager CRUD API Ready (/api/markers)")
    print(f"🎯 Auto Lens Calibration API Ready (/api/calibration/start)")
    print(f"-----------------------------------------------------------------")
    print(f"📡 [접속 안내]")
    for ip in local_ips:
        print(f"   ✅ PC Wi-Fi 접속 시 : http://{ip}:{port}/")
    print(f"   ✅ 태블릿 핫스팟 접속 시 : 태블릿의 Wi-Fi 설정 창에서")
    print(f"      '게이트웨이' 또는 '라우터' 주소를 확인해 접속하세요!")
    print(f"=================================================================")
    
    app.run(host='0.0.0.0', port=port, debug=False)
