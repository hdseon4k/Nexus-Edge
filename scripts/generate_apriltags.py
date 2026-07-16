import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import argparse
import os

def create_apriltag_image(tag_id):
    # A4 size in pixels at 300 DPI
    A4_WIDTH = 2480
    A4_HEIGHT = 3508
    
    # Generate the AprilTag (tag36h11)
    # OpenCV 4.7+ moved aruco to cv2.aruco directly
    try:
        # Modern OpenCV (4.7+)
        dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36h11)
        tag_image = cv2.aruco.generateImageMarker(dictionary, tag_id, 300, 1)
    except AttributeError:
        # Older OpenCV or contrib
        dictionary = cv2.aruco.Dictionary_get(cv2.aruco.DICT_APRILTAG_36h11)
        tag_image = np.zeros((300, 300), dtype=np.uint8)
        tag_image = cv2.aruco.drawMarker(dictionary, tag_id, 300, tag_image, 1)

    # Convert to PIL Image
    pil_tag = Image.fromarray(tag_image).convert("RGB")
    
    # Scale up the tag using NEAREST to preserve sharp edges
    target_tag_size = 1600 
    pil_tag = pil_tag.resize((target_tag_size, target_tag_size), Image.Resampling.NEAREST)
    
    # Create A4 white canvas
    canvas = Image.new('RGB', (A4_WIDTH, A4_HEIGHT), 'white')
    draw = ImageDraw.Draw(canvas)
    
    # Define cutting box size (square)
    cut_size = 2100
    
    # Calculate cutting box position (centered on A4)
    box_x = (A4_WIDTH - cut_size) // 2
    box_y = (A4_HEIGHT - cut_size) // 2
    
    # Draw the cutting outline (light gray, thin line)
    draw.rectangle(
        [box_x, box_y, box_x + cut_size, box_y + cut_size],
        outline="gray",
        width=4
    )
    
    # Calculate position to paste the tag inside the cutting box
    tag_x = box_x + (cut_size - target_tag_size) // 2
    tag_y = box_y + 150
    
    # Paste the tag onto the canvas
    canvas.paste(pil_tag, (tag_x, tag_y))
    
    # Try to load Windows default Arial font, fallback if not found
    try:
        font = ImageFont.truetype("arial.ttf", 90)
    except IOError:
        try:
            # Mac/Linux fallback
            font = ImageFont.truetype("DejaVuSans.ttf", 90)
        except IOError:
            font = ImageFont.load_default()
    
    text = f"AprilTag (tag36h11) - ID: {tag_id}"
    
    # Get bounding box for text to center it
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
    except AttributeError:
        # Older Pillow versions
        text_w, text_h = draw.textsize(text, font=font)
        
    text_x = box_x + (cut_size - text_w) // 2
    text_y = tag_y + target_tag_size + 120
    
    # Draw the human-readable ID
    draw.text((text_x, text_y), text, fill="black", font=font)
    
    return canvas

def create_charuco_board_image():
    # A4 size in pixels at 300 DPI
    A4_WIDTH = 2480
    A4_HEIGHT = 3508
    
    # Board settings: 7x10 squares fits nicely on A4
    squaresX = 7
    squaresY = 10
    
    # The ratio of marker length to square length. 
    # Physical size doesn't matter here for image generation, only the ratio.
    squareLength = 0.04 
    markerLength = 0.03 
    
    # Calculate exact pixel dimensions to ensure squares remain perfect squares
    # Let 1 square = 300 pixels (approx 2.54 cm at 300 DPI)
    square_px = 300
    board_width = squaresX * square_px
    board_height = squaresY * square_px
    
    try:
        # Modern OpenCV (4.7+)
        dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_100)
        board = cv2.aruco.CharucoBoard((squaresX, squaresY), squareLength, markerLength, dictionary)
        board_img_cv = board.generateImage((board_width, board_height), marginSize=0, borderBits=1)
    except AttributeError:
        # Older OpenCV or contrib
        dictionary = cv2.aruco.Dictionary_get(cv2.aruco.DICT_5X5_100)
        board = cv2.aruco.CharucoBoard_create(squaresX, squaresY, squareLength, markerLength, dictionary)
        board_img_cv = board.draw((board_width, board_height), marginSize=0, borderBits=1)

    pil_board = Image.fromarray(board_img_cv).convert("RGB")
    
    # Create A4 white canvas
    canvas = Image.new('RGB', (A4_WIDTH, A4_HEIGHT), 'white')
    
    # Center the board on the canvas
    box_x = (A4_WIDTH - board_width) // 2
    box_y = (A4_HEIGHT - board_height) // 2 - 50 # Shift slightly up for text
    
    canvas.paste(pil_board, (box_x, box_y))
    
    draw = ImageDraw.Draw(canvas)
    
    try:
        font = ImageFont.truetype("arial.ttf", 70)
    except IOError:
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", 70)
        except IOError:
            font = ImageFont.load_default()
            
    text = f"ChArUco Board (5x5_100) - {squaresX}x{squaresY} squares"
    
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
    except AttributeError:
        text_w, text_h = draw.textsize(text, font=font)
        
    text_x = (A4_WIDTH - text_w) // 2
    text_y = box_y + board_height + 80
    
    draw.text((text_x, text_y), text, fill="black", font=font)
    
    return canvas

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a single multipage AprilTag tag36h11 PDF on A4 paper")
    parser.add_argument("--start", type=int, default=0, help="Start ID (e.g. 0)")
    parser.add_argument("--count", type=int, default=5, help="Number of tags to generate")
    parser.add_argument("--out", type=str, default="AprilTag36h11_Merged.pdf", help="Output PDF file path")
    args = parser.parse_args()
    
    print(f"Generating {args.count} tags starting from ID {args.start}...")
    pages = []
    for i in range(args.start, args.start + args.count):
        print(f"Processing ID {i}...")
        pages.append(create_apriltag_image(i))
        
    print("Appending ChArUco Calibration Board to the final page...")
    pages.append(create_charuco_board_image())
    
    # Save as a single multipage PDF
    output_path = args.out
    # Ensure directory exists if path has one
    out_dir = os.path.dirname(os.path.abspath(output_path))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    
    if pages:
        pages[0].save(
            output_path, 
            "PDF", 
            resolution=300.0, 
            save_all=True, 
            append_images=pages[1:]
        )
        print(f"Done! All tags and the calibration board saved into a single file: {os.path.abspath(output_path)}")
