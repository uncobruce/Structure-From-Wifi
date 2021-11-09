import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon, MultiPoint
import numpy as np
import cv2
import math
from bresenham import bresenham
import kvisibility_floorplan
import random_trajectory
from shapely.ops import polygonize
from shapely.ops import cascaded_union
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
routery, routerx = int((desired_height)*kvisibility_floorplan.routery/maxcoordy), int((desired_height+30)*kvisibility_floorplan.routerx/maxcoordx)
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

k2vals = getkValCoordinates(trajectoryKValueDictionary, 2)
k3vals = getkValCoordinates(trajectoryKValueDictionary, 3)
k4vals = getkValCoordinates(trajectoryKValueDictionary, 4)
k5vals = getkValCoordinates(trajectoryKValueDictionary, 5)

# Get router point
routerpt = (routerx,routery)
    
# Seperate trajectory into different segments based on if they are continuous and have same kval
trajectorySegmentsList = []
i=0
coordinates_count=0
while i < len(trajectoryCoordinates):
    coord = trajectoryCoordinates[i]
    if i == 0:
        comparisonKValue = trajectoryKValueDictionary[coord]
        currentKValue = comparisonKValue
    singleSegmentList = []
    while currentKValue == comparisonKValue and i < len(trajectoryCoordinates):
        coord = trajectoryCoordinates[i]
        singleSegmentList.append(coord)
        coordinates_count+=1
        currentKValue = trajectoryKValueDictionary[coord]
        i+=1
    trajectorySegmentsList.append(singleSegmentList)
    
    comparisonKValue = currentKValue
k_val_dictionary = getKValueDictionary(trajectoryKValueDictionary)

assert coordinates_count == len(trajectoryCoordinates), "Total number of coordinates in array [trajectorySegmentsList] must equal number of coordinates in array [trajectoryCoordinates]"

def getCornersofSegment(segment):
    ''' 
        Given a trajectory segment,
         find the beginning and end of the segment
         (a segment is a continuous straight line consisting of coordinates having the same k-value -
         therefore, beginning/end points are at the start/end of a line after a turn or when a new k-value
         is encountered).
    '''
    cornerpts = []
    for i in range(len(segment)-1):
        point1 = segment[i]
        point2 = segment[i+1]
        if point1 == segment[0]:
            cornerpts.append(point1)
            currentcorner = point1
            continue
        if point2[0] != currentcorner[0] and point1[0] == currentcorner[0]:
            cornerpts.append(point1)
            currentcorner = point2
        if point2[1] != currentcorner[1] and point1[1] == currentcorner[1]:
            cornerpts.append(point1)
            currentcorner = point2
    return cornerpts

def drawKValueCone(segment, routerpt):
    '''
    Given a trajectory segment,
        draw the k value polygon.
        '''
    cornerpts = getCornersofSegment(segment)
    totalcones = []
    for i in range(len(cornerpts)-1):
        corner1 = cornerpts[i]
        corner2 = cornerpts[i+1]
        line1 = (routerpt, corner1)
        line2 = (routerpt, corner2)
        line3 = (corner1, corner2)
        coneregion = list(polygonize((line1,line2, line3)))
        if coneregion != []:
            cone = coneregion[0]
            totalcones.append(cone)
    kregioncones = [cone for cone in totalcones]
    polygon_final = cascaded_union(kregioncones)
    return polygon_final


def drawPolygonsForKValue(kvalue, trajectorySegmentsList, k_val_dictionary, routerpt):
    ''' 
    Identify all segments given a certain k-value,
    and create all cone shape Polygon objects corresponding to each segment
    '''
    segmentstoDraw = []
    poly_k_vals=[]
    for segment in trajectorySegmentsList:
        segment_kvalue = k_val_dictionary[(segment[1][0], segment[1][1])] #first pt k value is seg kval
        if segment_kvalue == kvalue:
            segmentstoDraw.append(segment)    
    polygons = []
    for segment in segmentstoDraw:
        polygon = drawKValueCone(segment, routerpt)
        if polygon.geom_type == 'Polygon': # Some polys are recorded as Empty geometry collections
            polygons.append(polygon)
            poly_k_vals.append(kvalue)
    return polygons, poly_k_vals


kvalues = [0, 1, 2, 3, 4, 5]

ax=plt.gca()
ax.set_xlim(8, 73)
ax.set_ylim(8, 73)
facecolors=['red','yellow','blue','green','orange', 'magenta', 'navy', 'teal', 'tan', 'lightsalmon','lightyellow','coral','rosybrown']

all_kval_polygons = [] # list of all polygons created, from k_n --> k0
all_corresp_kvals = [] # corresp. k-values for every polygon created


# # Plot all cone shapes  (step 1)
for i in range(len(kvalues), -1, -1):
    kvalue = i 
    polygons, poly_k_vals = drawPolygonsForKValue(kvalue, trajectorySegmentsList, k_val_dictionary, routerpt)
    for poly in polygons:
        # kfill = PolygonPatch(poly,facecolor=facecolors[i])
        # ax.add_patch(kfill)    
        all_kval_polygons.append(poly)
        all_corresp_kvals.append(kvalue)
        
# Step 2. Remove all common parts k_1, ..., k_n polygons with all k_0 polygons
# ---------------------------------------------------------------------------------
def getConeShapesForKValue(kvalue, all_kval_polygons, all_corresp_kvals):
    ''' Given a desired k value, return all cone shapes with the same k value.'''
    coneshapeslist=[]
    for i in range(len(all_kval_polygons)):
        polygon, polygonkvalue = all_kval_polygons[i], all_corresp_kvals[i]
        if polygonkvalue == kvalue:
            coneshapeslist.append(polygon)
    return coneshapeslist        

k0polys = getConeShapesForKValue(0, all_kval_polygons, all_corresp_kvals)
k1polys = getConeShapesForKValue(1, all_kval_polygons, all_corresp_kvals)
k2polys = getConeShapesForKValue(2, all_kval_polygons, all_corresp_kvals)
k3polys = getConeShapesForKValue(3, all_kval_polygons, all_corresp_kvals)

# Create 2D array where every row is a list of kval polys w/corresp row index being k value
coneshapes_sorted = [i for i in range(len(kvalues))] # initialization
for i in range(len(kvalues)):
    coneshapes_sorted[i] = getConeShapesForKValue(i, all_kval_polygons, all_corresp_kvals)

differencepolys, differencepolyskvals =[], []

# I should automate this but this is ok for now
for cone in k0polys:
    differencepolys.append(cone)
    differencepolyskvals.append(0)
    for cone2 in k1polys:
        intersection = cone2.intersection(cone)
        if intersection.geom_type == 'Polygon': 
            print(intersection)
            diff = cone2.difference(cone)
            print(cone, cone2, "\n")
            diffcoords = diff.exterior.coords
            if routerpt not in diffcoords:
                differencepolys.append(diff)
                differencepolyskvals.append(1)

for cone in differencepolys:
    for cone2 in k2polys:
        intersection = cone2.intersection(cone)
        diff = cone2.difference(cone)
        if diff.geom_type == 'Polygon':
            diffcoords = diff.exterior.coords
            if routerpt not in diffcoords:
                differencepolys.append(diff)
                differencepolyskvals.append(2)

for cone in differencepolys:
    for cone2 in k3polys:
        intersection = cone2.intersection(cone)
        diff = cone2.difference(cone)
        if diff.geom_type == 'Polygon':
            diffcoords = diff.exterior.coords
            if routerpt not in diffcoords:
                differencepolys.append(diff)
                differencepolyskvals.append(3)
cone1 = differencepolys[3]
cone2 = k2polys[0]

ax2=plt.gca()
ax2.set_xlim(8, 73)
ax2.set_ylim(8, 73)

''' Plot intersection polygons for kvals: {1, ..., n}'''
for i in range(len(differencepolys)):
    poly = differencepolys[i]
    poly_kval = differencepolyskvals[i]
 #   if poly_kval != 3: continue
    colour = facecolors[poly_kval]
    kfill = PolygonPatch(poly,facecolor=colour)
    ax2.add_patch(kfill)    
plt.show()    



