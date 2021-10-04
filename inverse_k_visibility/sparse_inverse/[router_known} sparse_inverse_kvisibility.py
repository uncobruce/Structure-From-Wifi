import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon
import numpy as np
import cv2
import math
from bresenham import bresenham
import kvisibility_floorplan
import random_trajectory
from shapely.ops import polygonize
max_k0_visble_distance = 2
max_kval_visble_distance = 4

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
    plt.axis('off')
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
k0vals.append((routerx, routery)) # append routerpt to k0vals to avoid it being counted as a wall

k2vals = getkValCoordinates(trajectoryKValueDictionary, 2)
k3vals = getkValCoordinates(trajectoryKValueDictionary, 3)
k4vals = getkValCoordinates(trajectoryKValueDictionary, 4)

# Get router point
routerpt = (routerx,routery)

# Get map bounds
gridmapwidth, gridmapheight = random_trajectory.gridmapwidth,random_trajectory.gridmapheight

# Get grid bounds
kvisgridmapwidth,kvisgridmapheight = random_trajectory.kvisgridmapwidth, random_trajectory.kvisgridmapheight

# Get map paths
paths = random_trajectory.insidemappaths


# Sort k0 vals to be able to draw outline 
k0vals = sorted(k0vals, key=lambda k: (k[1], k[0])) #sort k0 vals by y coordinate
# --------------------------------------------------------------------
# # Fill k0 polygon 
# polypoints = []
# poly = Polygon(k0vals)
# for i in range(len(testmap)):
#     for j in range(len(testmap)):
#         point = Point(i,j)
#         if point.within(poly):
#             testmap[j][i] = 0
#             polypoints.append((i,j))
        
# # Draw outline of k0 polygon
# i=0
# linepoints=[]
# for k01 in k0vals:
#     point0 = k01
#     if i == len(k0vals)-1:
#         point1 = k0vals[0]
#     else:
#         point1 = k0vals[i+1]
#     i+=1
#     x0,y0 = point0[0], point0[1]
#     x1,y1 = point1[0], point1[1]
#     k0_line = list(bresenham(x0, y0, x1, y1))
#     for pt in k0_line:
#         ptx,pty = pt[0],pt[1]
#         testmap[pty][ptx] = 0
#         linepoints.append(pt)     
        
# # Add new k0 values to full k values list w/ corresp. k val       
# new_k0vals = linepoints + polypoints
# k0vals = new_k0vals


#-------------------------------------------------------------------
# Obtain dictionary containing every grid cell's k value
k_val_dictionary = getKValueDictionary(trajectoryKValueDictionary)
k_val_dictionary[(routerx,routery)] = 0


# print(checkAngleBetweenPoints((25,20),(25,10)))

# def collinear(x1, y1, x2, y2, x3, y3):
        
#     return 0 == x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2)


wallorFreeSpaceDict={}
def checkNeighbouringCells(k, currentkval, routerpt, testmap, max_kval_visble_distance, k_val_dictionary, trajectoryCoordinates, wallorFreeSpaceDict):
    for i in range(len(testmap)-1): # i is grid row
        for j in range(len(testmap[0])-1): # j is grid col in that row
            y, x = i, j
            cellkvalue = k_val_dictionary[(x,y)]
            linetoRouter = list(bresenham(x,y,routerpt[0],routerpt[1]))
            point1 = np.array((x,y))
            point2 = np.array(k)
            distanceToKValue = int(np.linalg.norm(point2-point1))
            if distanceToKValue <= 1 or distanceToKValue > max_kval_visble_distance: continue
            if (x,y) in trajectoryCoordinates: continue
            else:
                # if distanceToKValue <= max_kval_visble_distance // 2:
                #     if currentkval == 0:
                #         if cellkvalue == None:
                #             testmap[y][x] = 0
                #             k_val_dictionary[(x,y)] = currentkval
                #             wallorFreeSpaceDict[(x,y)] = 0
                # else:
                current_cell_value = testmap[y][x]
                same_kval_factor = 1 / (distanceToKValue) 
                current_cell_value = testmap[y][x]
                P_same_kval = current_cell_value * (1 - same_kval_factor)
                P_occ = (1 - (current_cell_value * (1 - same_kval_factor)))
                if cellkvalue == None :
                        testmap[y][x] = P_same_kval
                        k_val_dictionary[(x,y)] = currentkval
                        wallorFreeSpaceDict[(x,y)] = 0
                    # elif (cellkvalue == currentkval-1 or cellkvalue == currentkval+1) and (x,y) in linetoRouter:
                    #     testmap[y][x] = P_occ
                    #     k_val_dictionary[(x,y)] = currentkval
                    #     wallorFreeSpaceDict[(x,y)] = 1
                    #     return testmap, k_val_dictionary,wallorFreeSpaceDict
                    # elif cellkvalue == currentkval: continue
                    # else:
                    #     print('cellkvalue:',cellkvalue,'coords:',(j,i), 'currentkvalue:',currentkval)
                
    return testmap, k_val_dictionary, wallorFreeSpaceDict
                    
def updateGridMap(k_val_dictionary, currentkval, kvals, max_kval_visble_distance, testmap, trajectoryCoordinates, routerpt, wallorFreeSpaceDict):
    for k in kvals:
        testmap, k_val_dictionary, wallorFreeSpaceDict = checkNeighbouringCells(k, currentkval, routerpt, testmap, max_kval_visble_distance, k_val_dictionary, trajectoryCoordinates, wallorFreeSpaceDict)
        linetoRouter = list(bresenham(k[0],k[1],routerpt[0],routerpt[1]))
        for pt in linetoRouter:
            
            if k_val_dictionary[pt] == currentkval - 1 and currentkval !=0 and pt not in trajectoryCoordinates and testmap[pt[1]][pt[0]] !=0:
                testmap[pt[1]][pt[0]] = 1
                break
            elif currentkval == 0:
                testmap[pt[1]][pt[0]] = 0
                k_val_dictionary[pt] = currentkval
    # for i in range(len(testmap)):
    #     for j in range(len(testmap[0])):
    #         # if testmap[i][j] < 1:
    #         #     testmap[i][j] = 0
    #         testmap[i][j] = testmap[i][j]*1.05
    return testmap, k_val_dictionary, wallorFreeSpaceDict
       
plotGrid(testmap, desired_height+10, desired_width+10)
testmap, k_val_dictionary, wallorFreeSpaceDict = updateGridMap(k_val_dictionary, 0, k0vals, max_kval_visble_distance, testmap, trajectoryCoordinates, routerpt, wallorFreeSpaceDict)
testmap, k_val_dictionary, wallorFreeSpaceDict = updateGridMap(k_val_dictionary, 1, k1vals, max_kval_visble_distance, testmap, trajectoryCoordinates,  routerpt, wallorFreeSpaceDict)
testmap, k_val_dictionary, wallorFreeSpaceDict = updateGridMap(k_val_dictionary, 2, k2vals, max_kval_visble_distance, testmap, trajectoryCoordinates, routerpt, wallorFreeSpaceDict)
testmap, k_val_dictionary, wallorFreeSpaceDict = updateGridMap(k_val_dictionary, 3, k3vals, max_kval_visble_distance, testmap, trajectoryCoordinates,  routerpt, wallorFreeSpaceDict)
testmap, k_val_dictionary, wallorFreeSpaceDict = updateGridMap(k_val_dictionary, 4, k4vals, max_kval_visble_distance, testmap, trajectoryCoordinates,  routerpt, wallorFreeSpaceDict)
plotGrid(testmap, desired_height+10, desired_width+10)

# # a = [[1,2,3,4,5],[0,2,3,4,5]]
# # print(np.sum(a,axis=1).tolist()) #sum all rows

# # print(np.sum(a,axis=0).tolist()) #sum all cols

# # Remove all wall cells that are outside the bounds of the map
# outOfBoundsLength = (kvisgridmapwidth-gridmapwidth)//2

# # Four out of bounds area to clean up
# lowerBoundWidth, upperBoundWidth = kvisgridmapwidth, kvisgridmapwidth
# lowerBoundminHeight, lowerBoundmaxHeight = 0, outOfBoundsLength
# upperBoundminHeight, upperBoundmaxHeight = gridmapheight+outOfBoundsLength, kvisgridmapheight
# leftBoundHeight, rightBoundHeight = kvisgridmapheight, kvisgridmapheight
# leftBoundminWidth, leftBoundmaxWidth = 0, outOfBoundsLength
# rightBoundminWidth, rightBoundmaxWidth = gridmapwidth+outOfBoundsLength, kvisgridmapwidth

# for i in range(len(testmap)):
#     rowsum =  np.sum(testmap[i])
#     # print(i, rowsum)
#     if rowsum >= 50:
#         for j in range(len(testmap[0])):
#             if j > leftBoundmaxWidth and j < rightBoundminWidth and testmap[i][j] > 0 and testmap[i][j] < 1:
#                 testmap[i][j] = 1
#         # print('marking as wall')

# plotGrid(testmap, desired_height+10, desired_width+10)
# print('-------------------')
# colsum = np.sum(testmap,axis=0).tolist()
# startpt = np.where(testmap[i][j]==1,)
# for j in range(len(testmap[0])):
#     print(j, colsum[j])
#     if colsum[j] >= 40:
#         for i in range(len(testmap)):
#             if i > leftBoundmaxWidth and i < rightBoundminWidth and testmap[i][j] > 0 and testmap[i][j] < 1:
#                 testmap[i][j] = 1
#         print('marking col  as wall')
#     # elif colsum[j] >= 15 and colsum[j] < 40:
#     #     for i in range(len(testmap)):
#     #         if i > leftBoundmaxWidth and i < rightBoundminWidth and testmap[i][j] < 1:
#     #             if testmap[i][j] == 0:
    #                 break
    #             else:
    #                 testmap[i][j] = 1
                

# plotGrid(testmap, desired_height+10, desired_width+10)

for i in range(len(testmap)):
        for j in range(len(testmap[0])):
            if testmap[i][j] < 1:
                testmap[i][j] = 0
plotGrid(testmap, desired_height+10, desired_width+10)


# for pt in wallorFreeSpaceDict:
#     if wallorFreeSpaceDict[pt] == 0:
#         testmap[pt[1]][pt[0]] = 0


# Keep identified wall cells
# for i in range(len(testmap)-1):
#     for j in range(len(testmap[0])-1):
#         if testmap[i][j] < 0.75:
#             testmap[i][j] = 0
#         else:
#             testmap[i][j] = 1
        # if (j,i) in trajectoryCoordinates:
        #     testmap[i][j] = 0



# plotGrid(testmap, desired_height+10, desired_width+10)



# # Cleaning up out-of-bounds areas
# for i in range(lowerBoundminHeight, lowerBoundmaxHeight):
#     for j in range(lowerBoundWidth):
#         testmap[i][j] = 0
# for i in range(upperBoundminHeight+1, upperBoundmaxHeight):
#     for j in range(upperBoundWidth):
#         testmap[i][j] = 0
# for i in range(leftBoundHeight):
#     for j in range(leftBoundminWidth, leftBoundmaxWidth):
#         testmap[i][j] = 0        
# for i in range(rightBoundHeight):
#     for j in range(rightBoundminWidth+1, rightBoundmaxWidth):
#         testmap[i][j] = 0        





