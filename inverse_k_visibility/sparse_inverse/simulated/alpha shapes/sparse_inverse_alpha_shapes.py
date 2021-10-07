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

def makeLinesFromPointsList(pointslist):
        lineslist=[]
        for i in range(len(pointslist)):
            if i == len(pointslist)-1:
                pt1 = pointslist[i]
                pt2 = pointslist[0]
                line = (pt1,pt2)
                lineslist.append(line)
            else:
                pt1 = pointslist[i]
                pt2 = pointslist[i+1]
                line = (pt1,pt2)
                lineslist.append(line)
        return lineslist
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
    while currentKValue == comparisonKValue and i < len(trajectoryCoordinates):
        coord = trajectoryCoordinates[i]
        singleSegmentList.append(coord)
        currentKValue = trajectoryKValueDictionary[coord]
        i+=1
    trajectorySegmentsList.append(singleSegmentList)
    comparisonKValue = currentKValue

clusterpolys=[]
for segmentlist in trajectorySegmentsList:
    multipoint = MultiPoint(segmentlist)
    convexhull = multipoint.convex_hull
    if convexhull.geom_type == 'Polygon':
        plt.plot(*convexhull.exterior.xy)
        clusterpolys.append(convexhull)
    
def checkifPointinCluster(point, clusterpolys):
    p = Point(point)
    for poly in clusterpolys:
        if p.within(poly):
            return True
    return False

max_kval_visble_distance = 4
k_val_dictionary = getKValueDictionary(trajectoryKValueDictionary)
k_val_dictionary[(routerx,routery)] = 0
def checkNeighbouringCells(k, currentkval, routerpt, testmap, max_kval_visble_distance, k_val_dictionary, clusterpolys):
    for i in range(len(testmap)-1): # i is grid row
        for j in range(len(testmap[0])-1): # j is grid col in that row
            y, x = i, j
            point1 = np.array((x,y))
            point2 = np.array(k)
            distanceToKValue = int(np.linalg.norm(point2-point1))
            if distanceToKValue == 0: continue
            elif distanceToKValue > max_kval_visble_distance: continue
            elif checkifPointinCluster(point1, clusterpolys) == True: 
                continue
            else:
                current_cell_value = testmap[y][x]
                current_cell_kvalue = k_val_dictionary[(x,y)]
                same_kval_factor = 1 / distanceToKValue 
                current_cell_value = testmap[y][x]
                P_same_kval = current_cell_value * (1 - same_kval_factor)
                P_occ = (1 - (current_cell_value * (1 - same_kval_factor)))
                if current_cell_kvalue == None:
                    testmap[y][x] = P_same_kval 
                    k_val_dictionary[(x,y)] = currentkval
                elif current_cell_kvalue == currentkval-1  :
                       testmap[y][x] = P_occ +.2
                       k_val_dictionary[(x,y)] = currentkval
                       return testmap
       
    return testmap

plt.show()

def updateGridMap(k_val_dictionary, currentkval, kvals, max_kval_visble_distance, testmap, trajectoryCoordinates, routerpt):
    for k in kvals:
        testmap = checkNeighbouringCells(k, currentkval, routerpt, testmap, max_kval_visble_distance, k_val_dictionary, clusterpolys)
    return testmap

plotGrid(testmap, desired_height+10, desired_width+10)

testmap = updateGridMap(k_val_dictionary, 0, k0vals, max_kval_visble_distance, testmap, trajectoryCoordinates, routerpt)
testmap = updateGridMap(k_val_dictionary, 1, k1vals, max_kval_visble_distance, testmap, trajectoryCoordinates,  routerpt)
testmap = updateGridMap(k_val_dictionary, 2, k2vals, max_kval_visble_distance, testmap, trajectoryCoordinates, routerpt)
testmap = updateGridMap(k_val_dictionary, 3, k3vals, max_kval_visble_distance, testmap, trajectoryCoordinates,  routerpt)
testmap = updateGridMap(k_val_dictionary, 4, k4vals, max_kval_visble_distance, testmap, trajectoryCoordinates,  routerpt)

plotGrid(testmap, desired_height+10, desired_width+10)

all_coloured_coords = []
for i in range(len(testmap)-1): # i is grid row
    for j in range(len(testmap[0])-1): # j is grid col in that row
        if testmap[i][j] != 0.5:
            all_coloured_coords.append((j,i))
        

a = MultiPoint(all_coloured_coords)
boundingbox = a.convex_hull
boundx, boundy = boundingbox.exterior.xy
exterior_wall_coordinates = list(zip(boundx, boundy))
exterior_walls = makeLinesFromPointsList(exterior_wall_coordinates)
for wall in exterior_walls:
    startpt, endpt = (int(wall[0][0]), int(wall[0][1])), (int(wall[1][0]), int(wall[1][1]))
    coordinates = list(bresenham(startpt[0],startpt[1],endpt[0],endpt[1]))
    for coord in coordinates:
        testmap[coord[1]][coord[0]]=1
plotGrid(testmap, desired_height+10, desired_width+10)