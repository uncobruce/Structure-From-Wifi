import matplotlib.pyplot as plt
import kvisibility_floorplan
from shapely.geometry import  Point, Polygon, LineString
import numpy as np
import math
from shapely.ops import polygonize
from descartes import PolygonPatch
from shapely.ops import cascaded_union
import random
from bresenham import bresenham
import cv2

import heapq
# Import necessary variables from kvisibility_floorplan.py 
poly = kvisibility_floorplan.poly
routerPoint = kvisibility_floorplan.routerPoint
routerx, routery = kvisibility_floorplan.routerx, kvisibility_floorplan.routery
xmax, ymax = kvisibility_floorplan.xmax, kvisibility_floorplan.ymax
kvismap = cv2.imread('kvis_map_testroom.png')
gridmapwidth, gridmapheight = 70,70
kvisgridmapwidth,kvisgridmapheight = 80,80
def pixellateKVisibilityMap(kvismap, gridwidth, gridheight):
    # Get input size
    height, width = kvismap.shape[:2]
    
    # Desired "pixelated" size
    w, h = (gridwidth, gridheight)
    
    # Resize input to "pixelated" size
    temp = cv2.resize(kvismap, (w, h), interpolation=cv2.INTER_LINEAR)
    

    nrows, ncols, c = temp.shape # c is channel
    
    kvisgridmap = [[0 for x in range(nrows)] for y in range(ncols)]  
    for i in range(nrows):
        for j in range(ncols):
            b,g,r = (temp[i,j])
            kvisgridmap[-i][j] = (r,g,b)
    
    return kvisgridmap
def plotGrid(data, desired_height, desired_width):  
    fig, ax = plt.subplots()
    ax.imshow(data, cmap="Greys",origin="lower", vmax=1)
    ax.set_xticks(np.arange(desired_height+1)-0.5, minor=True)
    ax.set_yticks(np.arange(desired_width+1)-0.5, minor=True)
    ax.grid(which="minor")
    ax.tick_params(which="minor", size=0)
    plt.show()    

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

def initializeOccupancyGrid(desired_height, desired_width):
    data2 = np.zeros(desired_width*desired_height)
    data2 = data2.reshape((desired_width, desired_height))
    data2[data2 == 0 ] = 0
    return data2

# Create k visibility gridmap
kvisgridmap = pixellateKVisibilityMap(kvismap, kvisgridmapwidth, kvisgridmapheight)  
plotGrid(kvisgridmap, kvisgridmapwidth, kvisgridmapheight)

# Image of map to be recreated
img1 = cv2.imread("testroom.png")

# Create gridmap showing full map for comparison
gridmap = initializeOccupancyGrid(gridmapheight+10, gridmapwidth+10)
gridmap = imageToGrid(img1, gridmapheight, gridmapwidth, gridmap)
plotGrid(gridmap, gridmapwidth+10, gridmapheight+10)

def getRandomTrajectory(gridmap, startpt, endpt):
    # =======================================================================
    # Credit to Author: Christian Careaga (christian.careaga7@gmail.com)
    
    def heuristic(a, b):
        return np.sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2)
    
    
    def astar(array, start, goal):
        neighbors = [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]
        close_set = set()
        came_from = {}
        gscore = {start:0}
        fscore = {start:heuristic(start, goal)}
        oheap = []
        heapq.heappush(oheap, (fscore[start], start))
    
        while oheap:
            current = heapq.heappop(oheap)[1]
            if current == goal:
                data = []
                while current in came_from:
                    data.append(current)
                    current = came_from[current]
                return data
            close_set.add(current)
    
            for i, j in neighbors:
    
                neighbor = current[0] + i, current[1] + j
    
                tentative_g_score = gscore[current] + heuristic(current, neighbor)
    
                if 0 <= neighbor[0] < array.shape[0]:
    
                    if 0 <= neighbor[1] < array.shape[1]:                
    
                        if array[neighbor[0]][neighbor[1]] == 1:
    
                            continue
                    else:
                        # array bound y walls
                        continue
    
                else:
    
                    # array bound x walls
                    continue
                if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, 0):
                    continue
     
                if  tentative_g_score < gscore.get(neighbor, 0) or neighbor not in [i[1]for i in oheap]:
    
                    came_from[neighbor] = current
                    gscore[neighbor] = tentative_g_score
                    fscore[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                    heapq.heappush(oheap, (fscore[neighbor], neighbor))
    
        return False
    
    
    # =======================================================================

    path = astar(gridmap, (startpt[0],startpt[1]), (endpt[0],endpt[1]))
    actualpath=[]
    if path != False:
        for coord in path:
            x,y = coord[0],coord[1]
            gridmap[x][y] = 1
            actualpath.append((y,x))
        
    # TODO correlate k vals with trajectory vals
    # TODO create 4 paths outside of the map and 10 paths within the map
    # TODO move to sparse

    # plotGrid(gridmap, gridmapwidth+10, gridmapheight+10)
    return gridmap, path    
    
def plotStartPoint(xmin, xmax, ymin,ymax, gridmap):
        while True:
            x = random.randrange(xmin, xmax)
            y = random.randrange(ymin, ymax)
            point = (x,y)
            if (x > xmin and x < xmax) and (y > ymin and y < ymax) and (gridmap[x][y] != 1):
                return point, gridmap
            
def plotEndPoint(startpt,xmin, xmax, ymin,ymax, gridmap):
      print(xmin,xmax,ymin,ymax, 'endpt')
      while True:
        x = random.randrange(xmin, xmax)
        y = random.randrange(ymin, ymax)
        point = (x,y)
        if (x > xmin and x < xmax) and (y > ymin and y < ymax) and (gridmap[y][x] != 1) and (x != startpt[0] and y != startpt[1]):
            return point, gridmap
        

insidemappaths = []
# Plot 10 paths within the map
for i in range(15):
    startpt, gridmap = plotStartPoint(0, gridmapwidth,0, gridmapheight, gridmap)
    endpt, gridmap = plotEndPoint(startpt, 0,gridmapwidth, 0,gridmapheight, gridmap)   
    gridmap, path = getRandomTrajectory(gridmap, startpt, endpt)
    insidemappaths.append(path)

outOfMapPathPoints=[((0,5), (0,80)),
                    ((0,80),(0,5)),
                    ((75,80),(0,80)),
                     ((0,80),(75,80))]
outofmappaths= []
for pointset in outOfMapPathPoints:
    for i in range(3):
        x1, x2 = pointset[0][0], pointset[0][1]
        y1, y2 = pointset[1][0], pointset[1][1]
        
        if x1 < x2:
            xmin, xmax = x1, x2
        else:
            xmin, xmax = x2, x1
        
        if y1 < y2:
            ymin, ymax = y1, y2
        else:
            ymin, ymax = y2, y1
        
        startpt, gridmap = plotStartPoint(xmin, xmax, ymin, ymax, gridmap)
        endpt, gridmap = plotEndPoint(startpt, xmin,xmax, ymin,ymax, gridmap)   
        gridmap, path = getRandomTrajectory(gridmap, startpt, endpt)
        outofmappaths.append(path)
plotGrid(gridmap, gridmapwidth+10, gridmapheight+10)