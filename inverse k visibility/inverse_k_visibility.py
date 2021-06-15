import math
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import numpy as np
import pandas as pd
import cv2
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 


img = cv2.imread("visible_map.png")

# # RGB values:
# k0 = [237, 28, 36]
# k1 = [255, 242, 0]
# k2 = [63, 72, 204]
# k3 = [34, 177, 76]
# k4 = [127, 127, 127]

# BGR values:
k0 = np.array([36, 28, 237])
k1 = np.array([0, 242, 255])
k2 = np.array([204, 72, 63])
k3 = np.array([76, 177, 34])
k4 = np.array([127, 127, 127])
white = np.array([255, 255, 255])

blue, green, red = cv2.split(img)

numRows, numCols, c = img.shape # c is channel

mapCoordinates = []

for i in range(1, numRows):
    for j in range(1, numCols-3):
       
        pixel1 = img[i][j]
        pixel3 = img[i][j+3]
        if (np.array_equal(pixel1, k0) and np.array_equal(pixel3, k1)) or\
        (np.array_equal(pixel1, k1) and np.array_equal(pixel3, k0)):
            mapCoordinates.append((j, i))

         
        if (np.array_equal(pixel1, k1) and np.array_equal(pixel3, k2)) or\
        (np.array_equal(pixel1, k2) and np.array_equal(pixel3, k1)):
            mapCoordinates.append((j, i))
            
        if (np.array_equal(pixel1, k2) and np.array_equal(pixel3, k3)) or\
        (np.array_equal(pixel1, k3) and np.array_equal(pixel3, k2)):
            mapCoordinates.append((j, i))
            
        if (np.array_equal(pixel1, k3) and np.array_equal(pixel3, k4)) or\
        (np.array_equal(pixel1, k4) and np.array_equal(pixel3, k3)):
            mapCoordinates.append((j, i))
        
        if (np.array_equal(pixel1, k4) and np.array_equal(pixel3, white)) or\
        (np.array_equal(pixel1, white) and np.array_equal(pixel3, k4)):
            mapCoordinates.append((j, i))

            
for i in range(1, numRows-3):
    for j in range(1, numCols):
       
        pixel1 = img[i][j]
        pixel3 = img[i+3][j]
        if (np.array_equal(pixel1, k0) and np.array_equal(pixel3, k1)) or\
        (np.array_equal(pixel1, k1) and np.array_equal(pixel3, k0)):
            mapCoordinates.append((j, i))

         
        if (np.array_equal(pixel1, k1) and np.array_equal(pixel3, k2)) or\
        (np.array_equal(pixel1, k2) and np.array_equal(pixel3, k1)):
            mapCoordinates.append((j, i))
            
        if (np.array_equal(pixel1, k2) and np.array_equal(pixel3, k3)) or\
        (np.array_equal(pixel1, k3) and np.array_equal(pixel3, k2)):
            mapCoordinates.append((j, i))
            
        if (np.array_equal(pixel1, k3) and np.array_equal(pixel3, k4)) or\
        (np.array_equal(pixel1, k4) and np.array_equal(pixel3, k3)):
            mapCoordinates.append((j, i))
        
        if (np.array_equal(pixel1, k4) and np.array_equal(pixel3, white)) or\
        (np.array_equal(pixel1, white) and np.array_equal(pixel3, k4)):
            mapCoordinates.append((j, i))
            
cv2.circle(img, (89, 500), 6, (0, 0, 0), -1)           
for coords in mapCoordinates:
    x, y = coords[0], coords[1]
    cv2.circle(img, (x, y), 6, (0, 0, 0), -1)
cv2.imshow('polygon', img)
cv2.waitKey()
cv2.destroyAllWindows()
