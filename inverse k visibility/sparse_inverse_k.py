import matplotlib.pyplot as plt
import numpy as np
import cv2
max_kval_visble_distance = 3

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
    data[data == 0] = 0.5
    mapCoordinates.sort()
    mapCoordinates=np.array(mapCoordinates)
    for coords in mapCoordinates:
        mapx, mapy = coords[0],coords[1]
        data[mapy][mapx] = 1
    
    return data

def plotGrid(data, desired_height, desired_width):  
    fig, ax = plt.subplots()
    ax.imshow(data, cmap="Greys", origin="lower", vmax=1)
    ax.set_xticks(np.arange(desired_height+1)-0.5, minor=True)
    ax.set_yticks(np.arange(desired_width+1)-0.5, minor=True)
    ax.grid(which="minor")
    ax.tick_params(which="minor", size=0)
    plt.show()
    
def initializeOccupancyGrid(desired_height, desired_width):
    data2 = np.zeros(desired_width*desired_height)
    data2 = data2.reshape((desired_width, desired_height))
    data2[data2 == 0 ] = 0.5
    return data2

def plotKCoordinates(coordinates, data):
    for coords in coordinates:
        x,y=coords[0], coords[1]
        data[y][x] = 0
    return data

def getkValCoordinates(coordinates, kVals, desiredKValue):
    # Given a k value, return all coordinates that match this k value
    kValCoordinates = []
    for i in range(len(coordinates)):
        if kVals[i] == desiredKValue:
            kValCoordinates.append(coordinates[i])
    kValCoordinates.sort()
    return kValCoordinates

def getKValue(point, kvalCoords, kVals):
    # Given a point, return its k value
    for i in range(len(kvalCoords)):
        if kvalCoords[i] == point:
            return kVals[i]
        
def checkRow(data, row, col, kValue, kValueCoords, kVals, routery):
    # Return True if k-1 points on same row found
    x = col
    y = row
    if y == routery:
        return True
    for i in range(len(data[0])):
        if i == x:
            continue
        if data[y][i] != 0: # changing x values
            kval = getKValue((i,y), kValueCoords, kVals)
            if kval == kValue - 1:
                return True
    return False

def checkColumn(data, row, col, kValue, kValueCoords, kVals, routerx):
    # Return True if k-1 points on same col found
    x = col
    y = row
    if x == routerx:
        return True
    for i in range(len(data[0])):
        if i == y:
            continue
        if data[i][x] != 0: # changing y values
            kval = getKValue((x, i), kValueCoords, kVals)
            if kval == kValue - 1:
                return True
    return False


def getNearestYDistance(data, point, kPrevCoords, routery):
    # Compare nearest k-1 value by y-coordinate to router y coord
    # Return y value of whichever is closer to given point
    y = point[1]
    routerDiff = routery - y
    lowest_kDiff = None
    for k in kPrevCoords:
        ky = k[1]
        kDiff = ky - y
        if lowest_kDiff is None:
            lowest_kDiff = kDiff
        if kDiff < lowest_kDiff:
            lowest_kDiff = kDiff
        # print(lowest_kDiff, routerDiff)
    if abs(lowest_kDiff) < abs(routerDiff):
        return lowest_kDiff
    return routerDiff

def getNearestXDistance(data, point, kPrevCoords, routerx):
    x = point[0]
    routerDiff = routerx - x
    lowest_kDiff = None
    for k in kPrevCoords:
        kx = k[0]
        kDiff = kx - x
        if lowest_kDiff is None:
            lowest_kDiff = kDiff
        if kDiff < lowest_kDiff:
            lowest_kDiff = kDiff
    if abs(kDiff) < abs(routerDiff):
        return kDiff
    return routerDiff
# Coordinates of sparse k value points
kValueCoords=[(40, 56), (42, 58), (50,54), (35,55), \
              (42, 7),(37, 7),(57, 40), (55, 38),\
             (42, 40), (45, 38), (38, 15)] 
    # coords are plotted as (y, x)
    
# k values corresponding to every coordinate
kVals = [1,1,1,1, \
         1,1,1,1,\
         0, 0, 0]
    
# Desired grid map dimensions   
desired_height = 60
desired_width = 60

# Image of map to be recreated
img1 = cv2.imread("mapResult.jpg")

# Plot map and k value points for comparison
data = imageToGrid(img1, desired_height, desired_width)
routery, routerx = 47,37
data[routery][routerx] = 0.75 # transmitter point
data = plotKCoordinates(kValueCoords, data)
plotGrid(data, desired_height, desired_width)



# Create and plot occupancy grid
data2 = initializeOccupancyGrid(desired_height, desired_width)
data2[routery][routerx] = 0 # transmitter point
data2 = plotKCoordinates(kValueCoords, data2)


# Separate k value coords into different lists
k1vals = getkValCoordinates(kValueCoords, kVals, 1)
k0vals = getkValCoordinates(kValueCoords, kVals, 0)


kValueCoords.append((routerx,routery))

# All cells with a k value are free space
for k in kValueCoords:
    for i in range(len(data2)): # i is grid row
        for j in range(len(data2[0])): # j is grid col in that row
            current_cell_value = data2[i][j]
            y, x = i, j
            point1 = np.array((x, y))
            point2 = np.array(k)
            distanceToKValue = int(np.linalg.norm(point2-point1))
            if distanceToKValue > max_kval_visble_distance:
                continue # don't change cell value if outside max distance
            if distanceToKValue == 0:
                data2[i][j] = 0
            else:
                P_same_kval = 1 / distanceToKValue
                newCellValue = current_cell_value * (1 - P_same_kval)
                data2[i][j] = newCellValue
            
for i in range(len(data2)): # i is grid row
        for j in range(len(data2[0])): # j is grid col in that row
            current_cell_value = data2[i][j]
            print(current_cell_value)
         


plotGrid(data2, desired_height, desired_width)

