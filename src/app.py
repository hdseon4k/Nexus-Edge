from flask import Flask, render_template, Response, jsonify
from flask_cors import CORS
import cv2
import time
from inference.detector import AdvancedBarcodeDetector

app = Flask(__name__)
CORS(app)

# Initialize detector
# Note: Ensure yolo11n.pt is in the root or provide full path
detector = AdvancedBarcodeDetector(model_path="yolo11n.pt", use_zxing=True)

class VideoCamera:
    def __init__(self):
        self.video = cv2.VideoCapture(0)
    
    def __del__(self):
        self.video.release()
    
    def get_frame_with_inference(self):
        success, frame = self.video.read()
        if not success:
            return None, None
            
        # Process frame with our high-reliability detector
        detections = detector.detect_and_decode(frame)
        
        # Draw results on frame
        for det in detections:
            bbox = det['bbox']
            cv2.rectangle(frame, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), (0, 255, 0), 2)
            if det['decoded']:
                data = det['decoded']['data']
                engine = det['decoded']['engine']
                method = det['decoded']['method']
                cv2.putText(frame, f"{data} ({engine}/{method})", (int(bbox[0]), int(bbox[1]-10)), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Encode for streaming
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes(), detections

camera = VideoCamera()

@app.route('/')
def index():
    return app.send_static_file('index.html')

def gen(camera):
    while True:
        frame, _ = camera.get_frame_with_inference()
        if frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        else:
            time.sleep(0.1)

@app.route('/video_feed')
def video_feed():
    return Response(gen(camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/detections')
def detections():
    _, current_detections = camera.get_frame_with_inference()
    return jsonify(current_detections)

if __name__ == '__main__':
    # Run server
    app.run(host='0.0.0.0', port=5000, threaded=True)
