import matplotlib.pyplot as plt
import kvisibility_floorplan
import vertices2
from shapely.geometry import  Point, Polygon, LineString
import numpy as np
import math
from shapely.ops import polygonize
from descartes import PolygonPatch
from shapely.ops import cascaded_union
import random
from bresenham import bresenham
import cv2
from matplotlib import colors

import heapq

# Import necessary variables from kvisibility_floorplan.py 
poly = kvisibility_floorplan.poly
routerPoint = kvisibility_floorplan.routerPoint
routerx, routery = kvisibility_floorplan.routerx, kvisibility_floorplan.routery
xmax, ymax = kvisibility_floorplan.xmax, kvisibility_floorplan.ymax
kvismap = cv2.imread('kvis_map_testroom.png')
gridmapwidth, gridmapheight = 70,70
kvisgridmapwidth,kvisgridmapheight = 80,80
kvaluescolordict = kvisibility_floorplan.kvaluescolordict

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
    data = np.zeros(desired_width*desired_height)
    data = data.reshape((desired_width, desired_height))
    data[data == 0 ] = 0
    return data

# Create k visibility gridmap
kvisgridmap = pixellateKVisibilityMap(kvismap, kvisgridmapwidth, kvisgridmapheight)  
plotGrid(kvisgridmap, kvisgridmapwidth, kvisgridmapheight)

# Image of map to be recreated
img1 = vertices2.img

# Create gridmap showing full map for comparison
gridmap = initializeOccupancyGrid(gridmapheight+10, gridmapwidth+10)
gridmap = imageToGrid(img1, gridmapheight, gridmapwidth, gridmap)

def plotPathGivenPoints(listofpoints, gridmap):
    linestoplot=[]
    for i in range(len(listofpoints)-1):
        p1 = listofpoints[i]
        p2 = listofpoints[i+1]
        line = list(bresenham(p1[0],p1[1], p2[0],p2[1]))
        linestoplot.append(line)
    for line in linestoplot:
        for point in line:
            gridmap[point[1]][point[0]] = 0.75
    return gridmap, linestoplot       
# listofpoints=[ (30, 20), 
#               (25, 10),
#               (15,10),
#               (8, 21),
#               (8,72),
#                 (10, 70),
#                 (15, 15),
#                 (16, 17),
#                 (15,72),
#                 (20,72),
#                 (30, 69),
#                 (20,15),
#                 (25,15),
#                 (30, 25),
#                 (33, 21),
#                 (40,15),
#                 (45, 10),
#                 (50, 9),
#                 (60, 10),
#                 (65,8),
#                 (70,10),
#                 (72,20),
#                 (50, 18),
#                 (45, 20),
#                 (46,35),
#                 (62, 30),
#                 (72,35),
#                 (72,38),
#                 (45,38),
#                 (45,42),
#                 (34,45),
#                 (37,71),
#                 (50,72),
#                 (52,45),
#                 (56,42),
#                 (55,55),
#                 (60,56),
#                 (62,42),
#                 (72,42),
#                 (70,72),
#                 (60,72),
#                 (63,58),
#                 (53,57),
#                 (54,72)
#               ]

listofpoints=[ (30, 20), 
              (30, 10),
              (10,10),
              
                (10, 72),
                
                (15,72),
                (30,72),
                
                (30,25),
          
               
                (33, 25),
                (34,9),
       
          
                (70, 10),
        
                (70,35),
              
     
                (45,35),
                (45,42),
                (34,42),
                (35,71),
                (55,72),
                (55,57),
                (60,57),
       
                (60,42),
                (72,42),
                (70,72),
                (60,72),
                (60,65),
         
              ]


#testroom3
# listofpoints=[ (30, 20), 
#               (30, 10),
#               (10,10),
              
#                 (10, 25),
                
#                 (60,22),
#                 (45, 11),
#                 (35,15),
                
#                 (33,45),
          
#                (20, 33),
#                 (10, 35),
#                 (9,70),
       
#                  (50, 65),
#                 (70, 68),
        
#                 (70,35),
              
     
#                 (67,33),
#                 (69,25),
#                 (72,15),
#                 (70,10),
#                 (65,9),
#                 (70,30),
#                 (40,32),
       
#                 # (60,42),
#                 # (72,42),
#                 # (70,72),
#                 # (60,72),
#                 # (60,65),
         
#               ]
gridmap, insidemappaths = plotPathGivenPoints(listofpoints, gridmap)

outOfMapPathPoints=[(2,3), (4,77), (78,78), (76,1),(3,3)
                     ]
outofmappaths= []
gridmap, outofmappaths = plotPathGivenPoints(outOfMapPathPoints, gridmap)

plotGrid(gridmap, gridmapwidth+10, gridmapheight+10)

trajectoryCoordinates = []
for path in insidemappaths:
    if path != False:
        for point in path:
            trajectoryCoordinates.append(point)
# for path in outofmappaths:
#     if path != False:
#         for point in path:
#             trajectoryCoordinates.append(point)

kvaluecolors_rgb = {}
for color in kvaluescolordict: 
    a = colors.to_rgba(color)
    color2 = (a[0]*255, a[1]*255,a[2]*255)
    kvaluecolors_rgb[color2] = kvaluescolordict[color]

pathandKVals = {}
count = 1
for point in trajectoryCoordinates:
    correspKValColor = kvisgridmap[point[1]][point[0]]
    if correspKValColor in kvaluecolors_rgb.keys():
        correspkvalue = kvaluecolors_rgb[correspKValColor]
        pathandKVals[point] = correspkvalue
        count+=1
    else:
        backtrack_index=0
        while correspKValColor not in kvaluecolors_rgb.keys():
            backtrack_index+=1
            similar_point = trajectoryCoordinates[trajectoryCoordinates.index(point) - backtrack_index]
            correspKValColor = kvisgridmap[similar_point[1]][similar_point[0]]
        correspkvalue = kvaluecolors_rgb[correspKValColor]
        pathandKVals[point] = correspkvalue
        count+=1