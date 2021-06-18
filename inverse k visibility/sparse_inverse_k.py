import math
import matplotlib.pyplot as plt
import numpy as np
import cv2
import warnings
import random

def imageToGrid(image, desired_height, desired_width):   
    # Return list of grid coordinates that match image of map 
    # -----------------------------------------------------------------------
    # Get input size
    height, width = img1.shape[:2]

    # Desired "pixelated" size
    w, h = (500, 500)

    # Resize input to "pixelated" size
    temp = cv2.resize(img1, (w, h), interpolation=cv2.INTER_LINEAR)
    
    # Initialize output image
    output = cv2.resize(temp, (desired_width, desired_height), interpolation=cv2.INTER_NEAREST)
    
    # Obtain coordinates of map points in image
    mapCoordinates = []
    for i in range(desired_height):
        for j in range(desired_width):
            pixel = output[i][j]
            if pixel[0] != 255:
                output[i][j][0], output[i][j][1], output[i][j][2] = 0,0,0
                mapCoordinates.append((j,-i))
            
    # Initialize grid array for rebuilding map into grid form
    data = np.zeros(desired_width*desired_height)
    data = data.reshape((desired_width, desired_height))
    mapCoordinates.sort()
    mapCoordinates=np.array(mapCoordinates)
    for coords in mapCoordinates:
        mapx, mapy = coords[0],coords[1]
        data[mapy][mapx] = 1
    
    return data

def plotGrid(data, desired_height, desired_width):  
    fig, ax = plt.subplots()
    ax.imshow(data, cmap="Greys", origin="lower", vmin=0)
    ax.set_xticks(np.arange(desired_height+1)-0.5, minor=True)
    ax.set_yticks(np.arange(desired_width+1)-0.5, minor=True)
    ax.grid(which="minor")
    ax.tick_params(which="minor", size=0)
    plt.show()
    
def initializeOccupancyGrid(desired_height, desired_width):
    data2 = np.zeros(desired_width*desired_height)
    data2 = data2.reshape((desired_width, desired_height))
    return data2

def plotKCoordinates(coordinates, data):
    for coords in coordinates:
        x,y=coords[0], coords[1]
        data[y][x] = 0.75 
    return data

def getkValCoordinates(coordinates, kVals, desiredKValue):
    # Given a k value, return all coordinates that match this k value
    kValCoordinates = []
    for i in range(len(coordinates)):
        if kVals[i] == desiredKValue:
            kValCoordinates.append(coordinates[i])
    kValCoordinates.sort()
    return kValCoordinates

def getKValue(point, kvalCoords, kVals):
    # Given a point, return its k value
    for i in range(len(kvalCoords)):
        if kvalCoords[i] == point:
            return kVals[i]
        
def checkRow(data, row, col, kValue, kValueCoords, kVals):
    # Return True if k-1 points on same row found
    x = col
    y = row
    for i in range(len(data[0])):
        if i == x:
            continue
        if data[y][i] != 0: # changing x values
            kval = getKValue((i,y), kValueCoords, kVals)
            if kval == kValue - 1:
                return True
    return False

def checkColumn(data, row, col, kValue, kValueCoords, kVals):
    # Return True if k-1 points on same col found
    x = col
    y = row
    for i in range(len(data[0])):
        if i == y:
            continue
        if data[i][x] != 0: # changing y values
            kval = getKValue((x, i), kValueCoords, kVals)
            if kval == kValue - 1:
                return True
    return False

        
# Coordinates of sparse k value points
kValueCoords=[(40, 56), (42, 58), (50,54), (35,55), \
             (42, 40), (45, 38), (38, 15)] 
    # coords are plotted as (y, x)
    
# k values corresponding to every coordinate
kVals = [1,1,1,1, \
         0, 0, 0]
    
# Desired grid map dimensions   
desired_height = 60
desired_width = 60

# Image of map to be recreated
img1 = cv2.imread("mapResult.jpg")

# Plot map and k value points for comparison
data = imageToGrid(img1, desired_height, desired_width)
routery, routerx = 47,37
data[routery][routerx] = 1 # transmitter point
data = plotKCoordinates(kValueCoords, data)
plotGrid(data, desired_height, desired_width)

# Create and plot occupancy grid
data2 = initializeOccupancyGrid(desired_height, desired_width)
data2 = plotKCoordinates(kValueCoords, data2)
data2[routery][routerx] = 1 # transmitter point

# Separate k value coords into different lists
k1vals = getkValCoordinates(kValueCoords, kVals, 1)
k0vals = getkValCoordinates(kValueCoords, kVals, 0)


def getNearestYCoordinate(data, point, row, col, kValue, kValueCoords, kVals, routery):
    # Compare nearest k-1 value by y-coordinate to router y coord
    # Return y value of whichever is closer to given point
    x, y = point[1], point[0]
    routerDifference = int(abs(y - routery))
    nearest_kVal_y = 0
    for i in range(len(data[0])):
        #print(data[i][col])
        if i == row:
            continue
        if data[i][col] != 0: 
            kval = getKValue((col, i), kValueCoords, kVals)
            if kval == kValue - 1:
                nearest_kVal_y = i
    kValDifference = int(abs(y - nearest_kVal_y))                
    if routerDifference >= kValDifference:
        return routery
    return nearest_kVal_y
    
# If there are issues, recheck checkRow or checkCol   
isolatedPoints = [] # list for points that don't see any (k-1) points\
wallCoords = []
for p in k1vals:
    # on same row or column
    row, col = p[1], p[0]
    # print(p)
    # print(checkRow(data2, row, col, 1, kValueCoords, kVals))
    # print(checkColumn(data2, row, col, 1, kValueCoords, kVals))
    # print("\n\n\n")
    checkrow = checkRow(data2, row, col, 1, kValueCoords, kVals)
    checkcol = checkColumn(data2, row, col, 1, kValueCoords, kVals)
    if checkcol is True:
        nearestY = getNearestYCoordinate(data2,p,row,col,1, kValueCoords, kVals, routery)
        distance = (nearestY - row)//2
        wally, wallx = row + distance, col
        data2[wally][wallx] = 1
        wallCoords.append((wallx,wally))
        for point in isolatedPoints:
            x, y = point[0], point[1]
            data2[wally][x] = 1
            wallCoords.append((x,wally))
        isolatedPoints=[]
    elif checkcol is False:
        isolatedPoints.append(p)
    if p == k1vals[-1]:
        for point in isolatedPoints:
            x, y = point[0], point[1]
            data2[wally][x] = 1
            wallCoords.append((x,wally))
        isolatedPoints=[]

plotGrid(data2, desired_height, desired_width)
