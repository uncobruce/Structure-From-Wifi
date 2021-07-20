import numpy as np
import cv2
from shapely.geometry import  Point, Polygon, LineString, LinearRing,MultiPoint
import matplotlib.pyplot as plt

#warnings.filterwarnings("ignore", category=DeprecationWarning) 

# Convert polygon image to grayscale
img = cv2.imread("testroom.png") # ensure image is in same directory
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
canny = cv2.Canny(gray, 120, 255, 1)
erode = cv2.erode(gray,None, iterations=5)
flipVertical = cv2.flip(gray, 0)
# Detecting vertices
corners = cv2.goodFeaturesToTrack(flipVertical,maxCorners=25, qualityLevel=0.15, minDistance=80, blockSize=15,useHarrisDetector=True, k=0.01)
corners = np.float32(corners)




f = open("mapCorners.txt", "w") # write coordinates to text file
for corner in corners:
    x, y = corner[0]
    x,y = int(x), int(y)
    f.write(str((x,y)))
    f.write("\n")
f.close()
ret, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

contours, hierarchy = cv2.findContours(flipVertical, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
cv2.drawContours(img, contours, -1, (0,255,0), 3)

for corner in corners:
    x, y = corner[0]
    x,y = int(x), int(y)
    cv2.circle(img, (x, y), 6, (255, 0, 0), -1) # colour in all vertices

# imS = cv2.resize(img, (960, 540))   
# cv2.imshow('polygon', imS)
# cv2.waitKey()
# cv2.destroyAllWindows()


