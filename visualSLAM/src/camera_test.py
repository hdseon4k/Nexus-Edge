import cv2
import time

def test_camera(index=0):
    cap = cv2.VideoCapture(index)
    if not cap.isOpened():
        print(f"Could not open camera with index {index}")
        return

    print(f"Camera {index} opened successfully.")
    print("Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break

        cv2.imshow('EOS M6 Mark II Test', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # EOS Webcam Utility usually shows up as index 1 if a built-in webcam exists.
    test_camera(1)
