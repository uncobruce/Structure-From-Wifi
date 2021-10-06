import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon, MultiPoint
import numpy as np
import cv2
import math
from bresenham import bresenham
import kvisibility_floorplan
import random_trajectory
from shapely.ops import polygonize
import alphashape
from descartes import PolygonPatch
def imageToGrid(image, desired_height, desired_width, data):   
    # Return list of grid coordinates that match image of map 
    # -----------------------------------------------------------------------
    # Get input size
    height, width = image.shape[:2]

    # Desired "pixelated" size
    w, h = (500, 500)

    # Resize input to "pixelated" size
    temp = cv2.resize(image, (w, h), interpolation=cv2.INTER_LINEAR)
    
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
            
    # Add map components (walls and obstacles) to grid map
    mapCoordinates.sort()
    mapCoordinates=np.array(mapCoordinates)
    
    for coords in mapCoordinates:
        mapx, mapy = coords[0],coords[1]
     
        data[mapy-5][mapx+5] = 1


    return data

def plotGrid(data, desired_height, desired_width):  
    fig, ax = plt.subplots()
    ax.imshow(data, cmap="Greys", origin="lower", vmax=1)
    ax.set_xticks(np.arange(desired_height+1)-0.5, minor=True)
    ax.set_yticks(np.arange(desired_width+1)-0.5, minor=True)
    ax.grid(which="minor")
    ax.tick_params(which="minor", size=0)    
    # plt.axis('off')
    plt.show()
    
def initializeOccupancyGrid(desired_height, desired_width):
    testmap = np.zeros(desired_width*desired_height)
    testmap = testmap.reshape((desired_width, desired_height))
    testmap[testmap == 0] = 0.5
    return testmap

def plotKCoordinates(coordinates, data):
    for coords in coordinates:
        x,y=coords[0], coords[1]
        data[y][x] = 0
    return data


def getkValCoordinates(trajectoryKValueDictionary, desiredKValue):
    # Given a k value, return all coordinates that match this k value
    kValCoordinates = []
    for key in trajectoryKValueDictionary.keys():
        if trajectoryKValueDictionary[key] == desiredKValue:
            kValCoordinates.append(key)
    kValCoordinates.sort()
    return kValCoordinates

# Create a dictionary of every coordinate and its k value
def getKValueDictionary(trajectoryKValueDictionary):  
    k_val_dictionary = {}
    for i in range(len(testmap)):
        for j in range(len(testmap[0])):
            coordinate = (j,i)
            k_val_dictionary[coordinate] = None
    for coord in trajectoryKValueDictionary:
        k_val_dictionary[coord] = trajectoryKValueDictionary[coord]
    return  k_val_dictionary


# Desired grid map dimensions   
desired_height = 70
desired_width = 70

# Obtain simulated trajectory coordinates scaled down to gridmap size
maxcoordx = kvisibility_floorplan.xmax
maxcoordy = kvisibility_floorplan.ymax

# Image of map to be recreated
img1 = random_trajectory.img1

# Create gridmap showing full map for comparison
floormap = initializeOccupancyGrid(desired_height+10, desired_width+10)

# Plot full gridmap with simulated trajectory path
floormap = imageToGrid(img1, desired_height, desired_width, floormap)

# Plot router point scaled down to grid size
routery, routerx = int((desired_height)*kvisibility_floorplan.routery/maxcoordy), int((desired_height)*kvisibility_floorplan.routerx/maxcoordx)
floormap[routery][routerx] = 1 # router point
plotGrid(floormap, desired_height+10, desired_width+10)

# Create and plot test occupancy grid
testmap = initializeOccupancyGrid(desired_height+10, desired_width+10)
testmap[routery][routerx] = 0.75 # router point

# Get trajectory coordinates and corresponding k values
trajectoryCoordinates = random_trajectory.trajectoryCoordinates
trajectoryKValueDictionary = random_trajectory.pathandKVals

# Plot trajectory coordinates on testmap
plotKCoordinates(trajectoryCoordinates, testmap)

# Separate k value coords into different lists
k1vals = getkValCoordinates(trajectoryKValueDictionary, 1)
k0vals = getkValCoordinates(trajectoryKValueDictionary, 0)
# k0vals.append((routerx, routery)) # append routerpt to k0vals to avoid it being counted as a wall

k2vals = getkValCoordinates(trajectoryKValueDictionary, 2)
k3vals = getkValCoordinates(trajectoryKValueDictionary, 3)
k4vals = getkValCoordinates(trajectoryKValueDictionary, 4)
k5vals = getkValCoordinates(trajectoryKValueDictionary, 5)

# Get router point
routerpt = (routerx,routery)

# Cluster coordinates within each k value list
def subClusterCoordinates(kvaluelist):
    kvaluelist = np.array(kvaluelist)
    plt.scatter(kvaluelist[:,0], kvaluelist[:,1])
    listofClusters=[]
    currentRow=0
    for i in range(len(kvaluelist)-1):
        coord1 = kvaluelist[i]
        coord2 = kvaluelist[i-1]
        distance = np.linalg.norm(coord1-coord2)
        # print(distance, coord1, coord2)
        if distance == 1 or i == 0 or coord1[0]==coord2[0] or coord1[1]==coord2[1]:
            print(distance, coord1, coord2)
            listofClusters[currentRow].append(coord1)
        else:
            currentRow+=1
            listofClusters[currentRow].append(coord1)
            
trajectorySegmentsList = []
# Create alpha shapes of each cluster
i=0
while i < len(trajectoryCoordinates):
    coord = trajectoryCoordinates[i]
    if i == 0:
        comparisonKValue = trajectoryKValueDictionary[coord]
        currentKValue = comparisonKValue
    singleSegmentList = []
    while currentKValue == comparisonKValue:
        coord = trajectoryCoordinates[i]
        singleSegmentList.append(coord)
        currentKValue = trajectoryKValueDictionary[coord]
        i+=1
    trajectorySegmentsList.append(singleSegmentList)
    comparisonKValue = currentKValue

for segmentlist in trajectorySegmentsList:
    multipoint = MultiPoint(segmentlist)
    convexhull = multipoint.envelope
    if convexhull.geom_type == 'Polygon':
        plt.plot(*convexhull.exterior.xy)
    
    


plt.show()
# Plot

# Apply probability dist to each cluster