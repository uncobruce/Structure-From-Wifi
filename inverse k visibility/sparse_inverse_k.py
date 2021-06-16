import math
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import numpy as np
import pandas as pd
import cv2
import warnings
import random

enviromap = cv2.imread("mapResult.jpg")
f = open("mapCoordinates.txt", "r")
mapCoordinates = []
lines = f.readlines()

# Get list of coordinate tuples from text file
for line in lines:
    start1, end1 = '(', ','
    start2, end2 = ' ', ')'
    x,y = int((line.split(start1))[1].split(end1)[0]),\
        int((line.split(start2))[1].split(end2)[0])
    coords = (x,y)
    mapCoordinates.append(coords)
img = cv2.imread("visible_map.png")

numRows, numCols, c = img.shape # c is channel

img2 = np.zeros([numRows,numCols,c],dtype=np.uint8)
img2.fill(255)

for coords in mapCoordinates:
    x, y = coords[0], coords[1]
    cv2.circle(img2, (x, y), 6, (0, 0, 0), -1)

transmitterX = 500
transmitterY = 200
cv2.circle(img2, (transmitterX, transmitterY), 6, (0, 0, 255), -1)

randomCoords = [(675, 50), (545, 60), (600, 55), (530, 57), (550, 150), (600, 180)]
kValues = [1, 1, 1, 1, 0, 0]
lowestYValueCoords = None


def getk0Coords(coordinates, kValues):
    k0vals = []
    for i in range(len(coordinates)):
        if kValues[i] == 0:
            k0vals.append(coordinates[i])
    return k0vals

def getk1Coords(coordinates, kValues):
    k1vals = []
    for i in range(len(coordinates)):
        if kValues[i] == 1:
            k1vals.append(coordinates[i])
    return k1vals

k1horizontalSpread = False
k0vals = getk0Coords(randomCoords, kValues)
k1vals = getk1Coords(randomCoords, kValues)

k1vals.sort()
k1vals = np.array(k1vals)
k1valsX, k1valsY = np.array(k1vals[:,0]), np.array(k1vals[:,1])

k0vals.sort()
k0vals = np.array(k0vals)
k0valsX, k0valsY = np.array(k0vals[:,0]), np.array(k0vals[:,1])

slope1, int1 = np.polyfit(k1valsX, k1valsY, 1)

eps = 0.1
if (abs(slope1) < eps):
    k1horizontalSpread = True
averagek1X, averagek1Y = int(np.mean(k1valsX)), int(np.mean(k1valsY))
averagek0X, averagek0Y = int(np.mean(k0valsX)), int(np.mean(k0valsY))

diffavgx, diffavgy = averagek1X - averagek0X, averagek1Y - averagek0Y
wallBelow = False
if abs(diffavgy) > abs(diffavgx):
    if diffavgy < 0:
        print('wall is below k1 points')
        wallBelow = True
    else:
        print(' wall is above k1 points')
else:
    if diffavgx < 0:
        print('wall is to the right of k1 points')
    else:
        print('wall is to the left of k1 points')
        
# cv2.circle(img2, (averagek1X, averagek1Y), 6, (0, 255, 0), -1)
# cv2.circle(img2, (averagek0X, averagek0Y), 6, (0, 255, 0), -1)

smallestY = None
smallestYCoords = None
if wallBelow is True:
    for coords in k1vals:
        x, y = coords[0], coords[1]
        if smallestY is None or y < smallestY:
            smallestY = y
            smallestYCoords = coords
for coords in k1vals:
    cv2.circle(img2, (coords[0], smallestY + 35), 6, (20, 255, 0), -1)

    
# Figure out which general direction the wall is
# Set minimum x or y depth according to point closest to wall
# Figure out which points are vertices


for coords in randomCoords:
    x, y = coords[0], coords[1]
    cv2.circle(img2, (x, y), 6, (255, 0, 0), -1)

cv2.imshow('mapResult', img2)
cv2.waitKey()
cv2.destroyAllWindows()

