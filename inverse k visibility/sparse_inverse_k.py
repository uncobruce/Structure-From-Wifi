import math
import matplotlib.pyplot as plt
import numpy as np
import cv2
import warnings
import random

def imageToGrid(image, desired_height, desired_width):   
    # Return list of grid coordinates that match image of map
    # ------------------------------------------------------------------
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
        data[mapx][mapy] = 1
    data = np.transpose(data)
    return data


desired_height = 60
desired_width = 60
img1 = cv2.imread("mapResult.jpg")
data = imageToGrid(img1, desired_height, desired_width)

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
# TODO: gridmap of k visible areas
data2 = np.zeros(desired_width*desired_height)
data2 = data2.reshape((desired_width, desired_height))

for coords in randomCoords:
    x,y=coords[0],coords[1]
    data2[x][y] = 0.75 
data2[routerx][routery] = 1 # transmitter point

data2 = np.transpose(data2)


# rowSums=[]
# for i in range(1, len(data2[0])-1, 3):
#     prevRow = data2[i-1]
#     currentRow=data2[i]
#     nextRow=data2[i+1]
#     # print(prevRow)
#     # print(currentRow)
#     # print(nextRow)
#     colSum = 0
#     for j in range(len(prevRow)):
#         if prevRow[j] != 0. :
#             col1 = prevRow[j]
#             col2 = currentRow[j]
#             col3 = nextRow[j]
#             colSum = col1 + col2 + col3
#             break
#     s1, s2, s3 =sum(prevRow), sum(currentRow), sum(nextRow)
#     rowsum = s1 + s2 + s3
#     rowSums.append(rowsum)
#     print(i-1, i, i+1, 'rowsum',rowsum, 'colsum',colSum)

# rowSums = rowSums[::-1] # reverse order so it's top to bottom

fig2, ax2 = plt.subplots()
ax2.imshow(data2, cmap="Greys", origin="lower", vmin=0)
ax2.set_xticks(np.arange(desired_height+1)-0.5, minor=True)
ax2.set_yticks(np.arange(desired_width+1)-0.5, minor=True)
ax2.grid(which="minor")
ax2.tick_params(which="minor", size=0)
plt.show()

# sum up row-wise for every 3 rows
# if sum > sum of first col
# horizontal spread is true
# if there are k values below horiz values: wall is below
# draw walls at every points identified, x = each points x, y = min val y
