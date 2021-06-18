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

def plotCoordinates(coordinates, data):
    for coords in coordinates:
        x,y=coords[0], coords[1]
        data[y][x] = 0.75 
    return data

# Coordinates of sparse k value points
randomCoords=[(40, 56), (42, 58), (50,54), (35,55), \
              (42, 40), (45, 38), (38, 15)]
    
# k values corresponding to every coordinate
kVals = [1,1,1, \
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
data = plotCoordinates(randomCoords, data)
plotGrid(data, desired_height, desired_width)


# Create and plot occupancy grid
data2 = initializeOccupancyGrid(desired_height, desired_width)
data2 = plotCoordinates(randomCoords, data2)
data2[routery][routerx] = 1 # transmitter point
plotGrid(data2, desired_height, desired_width)

