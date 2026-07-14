import cv2
import numpy as np

def generate_chessboard(rows=9, cols=6, square_size=100, output_path='chessboard.png'):
    """
    Generates a chessboard pattern image.
    rows, cols: Number of internal corners. 
    A (9,6) pattern has 10x7 squares.
    """
    # Number of squares is (rows+1) x (cols+1)
    img_rows = (rows + 1) * square_size
    img_cols = (cols + 1) * square_size
    
    # Create a white background
    chessboard = np.ones((img_cols, img_rows), dtype=np.uint8) * 255
    
    for i in range(cols + 1):
        for j in range(rows + 1):
            if (i + j) % 2 == 1:
                start_x = j * square_size
                start_y = i * square_size
                chessboard[start_y:start_y + square_size, start_x:start_x + square_size] = 0
                
    cv2.imwrite(output_path, chessboard)
    print(f"Chessboard pattern saved to {output_path}")
    print(f"Pattern size: {rows}x{cols} internal corners (10x7 squares)")

if __name__ == "__main__":
    # Defaulting to 9x6 internal corners as expected by src/calibrate.py
    generate_chessboard(9, 6, 100, 'chessboard.png')
