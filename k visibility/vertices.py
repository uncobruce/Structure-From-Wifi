import math
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import numpy as np
import pandas as pd
import cv2
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

# Convert polygon image to grayscale
img = cv2.imread("1.png") # ensure image is in same directory
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


# Detecting vertices of polygon
corners = cv2.goodFeaturesToTrack(gray, maxCorners=20, qualityLevel=0.01, minDistance=30, blockSize=5,useHarrisDetector=True, k=0.01)
corners = np.float32(corners)

for corner in corners:
    x, y = corner[0]
    cv2.circle(img, (x, y), 6, (0, 255, 0), -1) # colour in all vertices

print('number of vertices: ', len(corners))

cv2.imshow('polygon', img)
cv2.waitKey()
cv2.destroyAllWindows()
