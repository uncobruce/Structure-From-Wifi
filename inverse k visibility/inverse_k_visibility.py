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

img2 = np.zeros([numRows,numCols,c],dtype=np.uint8)
img2.fill(255)

def checkPixels(pixel1, pixel3, kval1, kval2):
    if (np.array_equal(pixel1, kval1) and np.array_equal(pixel3, kval2)) or\
        (np.array_equal(pixel1, kval2) and np.array_equal(pixel3, kval1)):
            return True
    return False

mapCoordinates = []

for i in range(1, numRows):
    for j in range(1, numCols-3):     
        pixel1 = img[i][j]
        pixel3 = img[i][j+3]
        
        if checkPixels(pixel1, pixel3, k0, k1) is True:
            mapCoordinates.append((j, i))            
            
        elif checkPixels(pixel1, pixel3, k1, k2) is True:
            mapCoordinates.append((j, i))
            
        elif checkPixels(pixel1, pixel3, k2, k3) is True:
            mapCoordinates.append((j, i))
            
        elif checkPixels(pixel1, pixel3, k3, k4) is True:
            mapCoordinates.append((j, i))
            
        elif checkPixels(pixel1, pixel3, k4, white) is True:
            mapCoordinates.append((j, i))
            
for i in range(1, numRows-3):
    for j in range(1, numCols):     
        pixel1 = img[i][j]
        pixel3 = img[i+3][j]
        
        if checkPixels(pixel1, pixel3, k0, k1) is True:
            mapCoordinates.append((j, i))
            
        elif checkPixels(pixel1, pixel3, k1, k2) is True:
            mapCoordinates.append((j, i))
            
        elif checkPixels(pixel1, pixel3, k2, k3) is True:
            mapCoordinates.append((j, i))
            
        elif checkPixels(pixel1, pixel3, k3, k4) is True:
            mapCoordinates.append((j, i))
            
        elif checkPixels(pixel1, pixel3, k4, white) is True:
            mapCoordinates.append((j, i))

f = open("mapCoordinates.txt", "w") # write coordinates to text file
for coords in mapCoordinates:
    x, y = coords[0], coords[1]
    cv2.circle(img2, (x, y), 6, (0, 0, 0), -1)
    f.write(str(coords))
    f.write("\n")
f.close()

cv2.imshow('mapResult', img2)
cv2.waitKey()
cv2.destroyAllWindows()
cv2.imwrite('mapResult.jpg', img2) # save map result

