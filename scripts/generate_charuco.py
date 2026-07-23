import cv2
import cv2.aruco as aruco

# Use DICT_5X5_100, which is standard for many charuco setups
dictionary = aruco.getPredefinedDictionary(aruco.DICT_5X5_100)
# 5 squares wide, 7 squares high, 0.04m square length, 0.02m marker length
board = aruco.CharucoBoard((5, 7), 0.04, 0.02, dictionary)
# Generate high res image
img = board.generateImage((1000, 1400), marginSize=50, borderBits=1)

cv2.imwrite('d:/GitHub/Nexus-Edge/src/static/charuco.png', img)
print("charuco.png generated.")
