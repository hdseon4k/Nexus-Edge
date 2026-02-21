import cv2
import numpy as np
import threading
import queue
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from ultralytics import YOLO
from pyzbar import pyzbar
from pyzxing import BarCodeReader

class AdvancedBarcodeDetector:
    def __init__(self, model_path="yolo11n.pt", use_zxing=True):
        """
        Initialize the Industrial-Grade Barcode Detector.
        Stage 1: YOLOv11n Localization
        Stage 2: Multi-threaded Preprocessing & Ensemble Decoding (ZBar + ZXing)
        """
        self.model = YOLO(model_path)
        self.use_zxing = use_zxing
        if self.use_zxing:
            self.zxing_reader = BarCodeReader()
        
        # Predefined workers for parallel decoding
        self.executor = ThreadPoolExecutor(max_workers=4)

    def _perspective_transform(self, image, box_coords):
        """
        Warp image to get a top-down view of the barcode (Perspective Correction).
        box_coords: [x1, y1, x2, y2, x3, y3, x4, y4] or similar
        Currently assumes standard bounding box [x1, y1, x2, y2] and adds margin.
        """
        x1, y1, x2, y2 = map(int, box_coords)
        margin = 10
        h, w = image.shape[:2]
        
        # Crop with margin
        x1 = max(0, x1 - margin)
        y1 = max(0, y1 - margin)
        x2 = min(w, x2 + margin)
        y2 = min(h, y2 + margin)
        
        crop = image[y1:y2, x1:x2]
        return crop

    def _decode_worker(self, img, method_name):
        """
        Worker thread function to decode using ZBar first, then ZXing as backup.
        """
        results = []
        
        # Try ZBar (Fast for 1D)
        zbar_decoded = pyzbar.decode(img)
        for obj in zbar_decoded:
            results.append({
                "data": obj.data.decode("utf-8"),
                "type": obj.type,
                "method": method_name,
                "engine": "ZBar"
            })
        
        # If ZBar fails and ZXing is enabled, try ZXing (Better for 2D/Damaged)
        if not results and self.use_zxing:
            # ZXing usually takes a file path or PIL image, but pyzxing can handle some numpy
            # We save temporary to memory buffer or use its internal conversion
            try:
                # pyzxing works best with actual image files or high-level wrappers
                # Here we use a simplified call; actual pyzxing might need a temporary file for reliability
                zx_results = self.zxing_reader.decode_array(img)
                for res in zx_results:
                    if 'raw' in res:
                        results.append({
                            "data": res['raw'].decode("utf-8") if isinstance(res['raw'], bytes) else res['raw'],
                            "type": res.get('format', 'UNKNOWN'),
                            "method": method_name,
                            "engine": "ZXing"
                        })
            except Exception as e:
                pass

        return results

    def _preprocess_variants(self, crop):
        """
        Generate multiple preprocessing versions of the cropped image.
        """
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        
        variants = []
        
        # Variant A: Original Grayscale
        variants.append((gray, "Original"))
        
        # Variant B: Adaptive Thresholding + Closing (Fix broken lines)
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        kernel = np.ones((3,3), np.uint8)
        closing = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        variants.append((closing, "AdaptiveThreshold_Closing"))
        
        # Variant C: Sharpening + 2x Upscaling (For small/blurry codes)
        sharpen_kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpened = cv2.filter2D(gray, -1, sharpen_kernel)
        upscaled = cv2.resize(sharpened, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        variants.append((upscaled, "Sharpen_Upscale"))
        
        # Variant D: Otsu Binarization + Erosion (Fix bleed/blurs)
        _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        erosion = cv2.erode(otsu, kernel, iterations=1)
        variants.append((erosion, "Otsu_Erosion"))
        
        return variants

    def detect_and_decode(self, frame):
        """
        Main pipeline: YOLO Detection -> Crop -> Multi-threaded Decodes
        """
        start_time = time.time()
        
        # Stage 1: Fast Localization
        yolo_results = self.model.predict(frame, classes=[0], conf=0.25, verbose=False)
        
        final_detections = []
        
        for res in yolo_results:
            boxes = res.boxes.xyxy.cpu().numpy()
            
            for box in boxes:
                # Stage 1.5: Crop and Preprocess
                crop = self._perspective_transform(frame, box)
                variants = self._preprocess_variants(crop)
                
                # Stage 2: Parallel Decoding (Winner-takes-all logic)
                found_data = None
                
                # We submit all variants to the pool
                futures = {self.executor.submit(self._decode_worker, img, name): name for img, name in variants}
                
                # Collect first successful result
                for future in as_completed(futures):
                    decode_results = future.result()
                    if decode_results:
                        found_data = decode_results[0] # Take first result from this worker
                        # In a true winner-takes-all, we'd cancel other futures here
                        # but Python's ThreadPoolExecutor doesn't support easy 'stop all others'
                        # So we just break and take the first one that finished with success
                        break
                
                detection = {
                    "bbox": box.tolist(),
                    "decoded": found_data if found_data else None,
                    "inference_time": time.time() - start_time
                }
                final_detections.append(detection)
                
        return final_detections

if __name__ == "__main__":
    # Test script
    detector = AdvancedBarcodeDetector()
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret: break
        
        detections = detector.detect_and_decode(frame)
        
        for det in detections:
            bbox = det['bbox']
            cv2.rectangle(frame, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), (0, 255, 0), 2)
            if det['decoded']:
                data = det['decoded']['data']
                engine = det['decoded']['engine']
                cv2.putText(frame, f"{data} ({engine})", (int(bbox[0]), int(bbox[1]-10)), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        cv2.imshow("Industrial Barcode Detector", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()
