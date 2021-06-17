from PIL import Image
import math
import matplotlib.pyplot as plt
import numpy as np
import cv2
import warnings
import random

# Open image map
img1 = cv2.imread("mapResult.jpg")

# Get input size
height, width = img1.shape[:2]

# Desired "pixelated" size
w, h = (500, 500)

# Resize input to "pixelated" size
temp = cv2.resize(img1, (w, h), interpolation=cv2.INTER_LINEAR)

desired_height = 60
desired_width = 60

# Initialize output image
output = cv2.resize(temp, (desired_width, desired_height), interpolation=cv2.INTER_NEAREST)

mapCoordinates = []
for i in range(desired_height):
    for j in range(desired_width):
        pixel = output[i][j]
        if pixel[0] != 255:
            output[i][j][0], output[i][j][1], output[i][j][2] = 0,0,0
            mapCoordinates.append((j,-i))
            
data = np.zeros(desired_width*desired_height)
data = data.reshape((desired_width, desired_height))
mapCoordinates.sort()
mapCoordinates=np.array(mapCoordinates)

for coords in mapCoordinates:
    mapy, mapx = coords[0],coords[1]
    data[mapx][mapy] = 1

fig, ax = plt.subplots()

randomCoords=[(40, 56), (42, 58), (50,54), (35,55), \
              (42, 40), (45, 38), (38, 15)]
for coords in randomCoords:
    x,y=coords[0],coords[1]
    data[y][x] = 0.75 
    
routery, routerx = 47,37
data[routery][routerx] = 1 # transmitter point

ax.imshow(data, cmap="Greys", origin="lower", vmin=0)
ax.set_xticks(np.arange(desired_height+1)-0.5, minor=True)
ax.set_yticks(np.arange(desired_width+1)-0.5, minor=True)
ax.grid(which="minor")
ax.tick_params(which="minor", size=0)
plt.show()



kVals = [1,1,1, \
         0, 0, 0]

data2 = np.zeros(desired_width*desired_height)
data2 = data2.reshape((desired_width, desired_height))
for coords in randomCoords:
    x,y=coords[0],coords[1]
    data2[y][x] = 0.75 
data2[routery][routerx] = 1 # transmitter point
       
fig2, ax2 = plt.subplots()

ax2.imshow(data2, cmap="Greys", origin="lower", vmin=0)
ax2.set_xticks(np.arange(desired_height+1)-0.5, minor=True)
ax2.set_yticks(np.arange(desired_width+1)-0.5, minor=True)
ax2.grid(which="minor")
ax2.tick_params(which="minor", size=0)
plt.show()

