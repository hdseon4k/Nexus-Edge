import numpy as np
import cv2
import glob
import yaml
import os

def calibrate(board_size=(9, 6), square_size=0.025, image_dir='calibration_images'):
    # Prepare object points (0,0,0), (1,0,0), (2,0,0) ....,(8,5,0)
    objp = np.zeros((board_size[0] * board_size[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:board_size[0], 0:board_size[1]].T.reshape(-1, 2)
    objp *= square_size

    objpoints = [] # 3d point in real world space
    imgpoints = [] # 2d points in image plane.

    images = glob.glob(os.path.join(image_dir, '*.jpg'))

    if not images:
        print(f"No images found in {image_dir}. Please capture calibration images first.")
        return

    for fname in images:
        img = cv2.imread(fname)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        ret, corners = cv2.findChessboardCorners(gray, board_size, None)

        if ret:
            objpoints.append(objp)
            imgpoints.append(corners)

            # Draw and display the corners
            cv2.drawChessboardCorners(img, board_size, corners, ret)
            cv2.imshow('img', img)
            cv2.waitKey(100)

    cv2.destroyAllWindows()

    if not objpoints:
        print("Could not find chessboard corners in any image.")
        return

    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

    if ret:
        data = {
            'camera_matrix': mtx.tolist(),
            'dist_coeff': dist.tolist(),
        }
        with open('calibration.yaml', 'w') as f:
            yaml.dump(data, f)
        print("Calibration successful. Saved to calibration.yaml")
    else:
        print("Calibration failed.")

if __name__ == "__main__":
    # Create directory if it doesn't exist
    if not os.path.exists('calibration_images'):
        os.makedirs('calibration_images')
        print("Created 'calibration_images' directory. Please put chessboard photos there and run again.")
    else:
        calibrate()
