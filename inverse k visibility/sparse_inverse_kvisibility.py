import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon
import numpy as np
import cv2
import math
from bresenham import bresenham
import kvisibility_floorplan
import random_trajectory

max_k0_visble_distance = 2
max_kval_visble_distance = 3
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
img1 = cv2.imread("testroom.png")

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
k5vals = getkValCoordinates(trajectoryKValueDictionary, 5)


# --------------------------------------------------------------------
# TODO fix k0 polygon fill
# # Sort k0 vals to be able to draw outline 
# k0vals = sorted(k0vals, key=lambda k: (k[1], k[0])) #sort k0 vals by y coordinate

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
# for k0 in new_k0vals:
#     if k0 not in k0vals:
#         trajectoryCoordinates.append(k0)
# k0vals = new_k0vals
#-------------------------------------------------------------------
# Obtain dictionary containing every grid cell's k value
k_val_dictionary = getKValueDictionary(trajectoryKValueDictionary)
k_val_dictionary[(routerx,routery)] = 0
# for k0 in k0vals:
#     for i in range(len(testmap)-1): # i is grid row
#         for j in range(len(testmap[0])-1): # j is grid col in that row
#             y, x = i, j
#             current_cell_value = testmap[y][x]
#             point1 = np.array((x, y))
#             point2 = np.array(k0)
#             distanceToKValue = int(np.linalg.norm(point2-point1))
#             if k0 == k0vals[0]:
#                 print(distanceToKValue)
#                 break
def getUnknownCoordinates(k_val_dictionary, currentkval):
    # return a list of all coords whose kvals are unknown
    unknowncoordinates=[]
    for coord in k_val_dictionary:
        if k_val_dictionary[coord] == None:
            unknowncoordinates.append(coord)
    return unknowncoordinates

def updateGridMap(k_val_dictionary, currentkval, kvals, max_kval_visble_distance, testmap, trajectoryCoordinates):
    # unknowncoordinates = getUnknownCoordinates(k_val_dictionary, currentkval)
    for k in kvals:
        for i in range(len(testmap)-1): # i is grid row
            for j in range(len(testmap[0])-1): # j is grid col in that row
                y, x = i, j
                cellkvalue = k_val_dictionary[(x,y)]
                point1 = np.array((x,y))
                point2 = np.array(k)
                distanceToKValue = int(np.linalg.norm(point2-point1))
                # if currentkval == 1:
                #     print(cellkvalue == currentkval-1, cellkvalue, currentkval)
                if distanceToKValue == 0: continue
                if distanceToKValue == 1: # high likelihood of being same kval (or if same occurs for k+1 val, then wall)                    
                    if cellkvalue == None or cellkvalue != (currentkval+1) or cellkvalue != (currentkval-1) :
                        # k_val_dictionary[(x,y)] = currentkval # set as same kval
                        testmap[y][x] = 0
                        
                    if cellkvalue == (currentkval-1) or cellkvalue == (currentkval+1):
                        # k_val_dictionary[(x,y)] = currentkval # very close to two consecutive kvals: set as a wall except if traj passing through
                        testmap[y][x] = 1
                        k_val_dictionary[(x,y)] = -1
                        # TODO only make wall if row/col are completely untraversed
                    
                else:
                    if distanceToKValue > max_kval_visble_distance: 
                        continue # out of range: can't say anything about cell kvalue
                    # between 0 and max visible distance: likelihood decreases w/increasing distance
                    same_kval_factor = 1 / distanceToKValue # likelihood of being same kval inversely prop. to distance
                    current_cell_value = testmap[y][x]
                    P_same_kval = current_cell_value * (1 - same_kval_factor)
                    P_occ = (1 - (current_cell_value * (1 - same_kval_factor)))
                    if  k_val_dictionary[(x,y)] == None or k_val_dictionary[(x,y)] != currentkval+1 or k_val_dictionary[(x,y)] != currentkval-1:
                        testmap[y][x] = P_same_kval+.1
                    if k_val_dictionary[(x,y)] == currentkval+1 or k_val_dictionary[(x,y)] == currentkval-1:
                        # k_val_dictionary[(x,y)] = currentkval # set as wall if overlapping with a k-1 or k+1 region
                        testmap[y][x] = P_occ+.2
                        k_val_dictionary[(x,y)] = -1
                k_val_dictionary[(x,y)] = currentkval
    for coord in trajectoryCoordinates:
        x, y = coord[0], coord[1]
        testmap[y][x] = 0
    return testmap
testmap = updateGridMap(k_val_dictionary, 0, k0vals, max_kval_visble_distance, testmap, trajectoryCoordinates)
testmap = updateGridMap(k_val_dictionary, 1, k1vals, max_kval_visble_distance, testmap, trajectoryCoordinates)
testmap = updateGridMap(k_val_dictionary, 2, k2vals, max_kval_visble_distance, testmap, trajectoryCoordinates)
testmap = updateGridMap(k_val_dictionary, 3, k3vals, max_kval_visble_distance, testmap, trajectoryCoordinates)
testmap = updateGridMap(k_val_dictionary, 4, k4vals, max_kval_visble_distance, testmap, trajectoryCoordinates)
testmap = updateGridMap(k_val_dictionary, 5, k5vals, max_kval_visble_distance, testmap, trajectoryCoordinates)

plotGrid(testmap, desired_height+10, desired_width+10)

for i in range(len(testmap)):
    for j in range(len(testmap[0])):
        if testmap[i][j] > 0.5:
            testmap[i][j] = testmap[i][j]*1.25
            
plotGrid(testmap, desired_height+10, desired_width+10)
