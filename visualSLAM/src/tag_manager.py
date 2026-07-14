import cv2
import numpy as np
from pupil_apriltags import Detector
import os

def generate_tags(ids, family='tag36h11', size=400):
    """
    Note: pupil-apriltags doesn't generate images. 
    We use this script as a placeholder to remind that tags need to be downloaded or generated.
    Standard tag images can be found at: https://github.com/AprilRobotics/apriltag-imgs
    """
    print("Standard AprilTag images should be downloaded from the official repository:")
    print(f"https://github.com/AprilRobotics/apriltag-imgs/tree/master/{family}")
    
    if not os.path.exists('tags'):
        os.makedirs('tags')
    
    print("\nAfter downloading, place them in the 'tags/' folder and measure their physical size accurately.")

if __name__ == "__main__":
    generate_tags(range(10))
