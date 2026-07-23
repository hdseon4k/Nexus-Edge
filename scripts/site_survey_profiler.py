"""
Site Survey Profiler Script for Setup A
Analyzes video/camera feed to count ORB/FAST visual keypoints per frame,
evaluating the effectiveness of 3M 766 safety tape and AprilTag placement.
"""

import sys
import time
import cv2
import numpy as np

def run_site_survey(source=0):
    print("=================================================================")
    print("🔍 Setup A Site Survey: Visual Feature Density Profiler Started")
    print("=================================================================")
    
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        print(f"❌ Error: Cannot open video source '{source}'")
        return

    # ORB Feature Detector
    orb = cv2.ORB_create(nfeatures=2000)
    fast = cv2.FastFeatureDetector_create(threshold=25)

    frame_count = 0
    total_orb_pts = 0
    total_fast_pts = 0

    print("Press 'q' to stop profiling and display final summary report...\n")

    start_time = time.time()
    try:
        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                break

            frame_count += 1
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # ORB Keypoints
            kp_orb = orb.detect(gray, None)
            num_orb = len(kp_orb)
            total_orb_pts += num_orb

            # FAST Keypoints
            kp_fast = fast.detect(gray, None)
            num_fast = len(kp_fast)
            total_fast_pts += num_fast

            # Draw keypoints on visualization frame
            vis_frame = cv2.drawKeypoints(frame, kp_orb, None, color=(0, 255, 0), flags=0)

            # Overlay stats
            status_text = f"Frame: {frame_count} | ORB Keypoints: {num_orb} | FAST Keypoints: {num_fast}"
            cv2.putText(vis_frame, status_text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            # Quality Assessment Banner
            if num_orb > 800:
                quality_str = "EXCELLENT FEATURE DENSITY (Safe for SLAM)"
                color = (0, 255, 0)
            elif num_orb > 400:
                quality_str = "MODERATE FEATURE DENSITY (3M Tape Recommended)"
                color = (0, 165, 255)
            else:
                quality_str = "POOR FEATURE DENSITY (High Drift Risk - Tape Required!)"
                color = (0, 0, 255)

            cv2.putText(vis_frame, f"SLAM Risk: {quality_str}", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

            cv2.imshow("Site Survey Feature Density Viewer", vis_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        pass

    elapsed_time = time.time() - start_time
    cap.release()
    cv2.destroyAllWindows()

    # Final Summary Report
    avg_orb = round(total_orb_pts / max(1, frame_count), 1)
    avg_fast = round(total_fast_pts / max(1, frame_count), 1)

    print("\n=================================================================")
    print("📊 SITE SURVEY FEATURE PROFILING REPORT SUMMARY")
    print("=================================================================")
    print(f"Total Analyzed Frames: {frame_count}")
    print(f"Elapsed Profiling Time: {round(elapsed_time, 2)} seconds")
    print(f"Average ORB Keypoints / Frame : {avg_orb}")
    print(f"Average FAST Keypoints / Frame: {avg_fast}")
    print("-----------------------------------------------------------------")
    if avg_orb > 800:
        print("✅ SUCCESS: The surveyed environment has rich visual features for VisualSLAM.")
    else:
        print("⚠️ ACTION REQUIRED: Feature points are low. Apply 3M 766 safety tape to rack pillars/walls.")
    print("=================================================================\n")

if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else 0
    run_site_survey(src)
