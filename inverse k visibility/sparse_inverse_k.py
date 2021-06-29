import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon
import numpy as np
import cv2
from bresenham import bresenham

max_k0_visble_distance = 3
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
        


# Coordinates of sparse k value points
kValueCoords=[(40, 56), (42, 58), (50,54), (35,55), \
              (42, 7),(37, 7),(57, 40), (55, 38), (55, 18), (56, 45),\
             (42, 40), (45, 38), (38, 15), (50,20), (45, 18)] 
    # coords are plotted as (y, x)
    
# k values corresponding to every coordinate
kVals = [1,1,1,1, \
         1,1,1,1,1, 1,\
         0, 0, 0, 0, 0]
    
# Desired grid map dimensions   
desired_height = 60
desired_width = 60

# Image of map to be recreated
img1 = cv2.imread("mapResult.jpg")

# Plot map and k value points for comparison
data = imageToGrid(img1, desired_height, desired_width)
routery, routerx = 47,37
data[routery][routerx] = 0 # transmitter point
data = plotKCoordinates(kValueCoords, data)

# Create and plot occupancy grid
data2 = initializeOccupancyGrid(desired_height, desired_width)
data2[routery][routerx] = 0 # transmitter point
data2 = plotKCoordinates(kValueCoords, data2)

            
# Separate k value coords into different lists
k1vals = getkValCoordinates(kValueCoords, kVals, 1)
k0vals = getkValCoordinates(kValueCoords, kVals, 0)
kValueCoords.append((routerx,routery))
k0vals.append((routerx, routery))

# Sort k0 vals to be able to draw outline 
k0vals = sorted(k0vals, key=lambda k: (k[1], k[0])) #sort k0 vals by y coordinate
polypoints = []
# Fill k0 polygon 
poly = Polygon(k0vals)
for i in range(len(data2)):
    for j in range(len(data2)):
        point = Point(i,j)
        if point.within(poly):
            data2[j][i] = 0
            polypoints.append((i,j))
        
# Draw outline of k0 polygon
i=0
linepoints=[]
for k01 in k0vals:
    point0 = k01
    if i == len(k0vals)-1:
        point1 = k0vals[0]
    else:
        point1 = k0vals[i+1]
    i+=1
    x0,y0 = point0[0], point0[1]
    
    x1,y1 = point1[0], point1[1]
    k0_line = list(bresenham(x0, y0, x1, y1))
    for pt in k0_line:
        ptx,pty = pt[0],pt[1]
        data2[pty][ptx] = 0
        linepoints.append(pt)        
new_k0vals = linepoints + polypoints
for k0 in new_k0vals:
    if k0 not in k0vals:
        kValueCoords.append(k0)
        kVals.append(0)
k0vals = new_k0vals

# Create a dictionary of every coordinate and its k value
def getKValueDictionary(kValueCoords, kVals):
    zip_iterator = zip(kValueCoords, kVals)
    dictionary1 = dict(zip_iterator)    
    other_coords =[]
    other_kvals = []
    for i in range(len(data2)):
        for j in range(len(data2)):
            coordinate = (j,i)
            
            
            if coordinate not in kValueCoords:
                
                kval = None
                other_coords.append(coordinate)
                other_kvals.append(kval)
    zip_iterator2 = zip(other_coords, other_kvals)
    dictionary2 = dict(zip_iterator2)
    def Merge(dict1, dict2):
        return(dict2.update(dict1))
    Merge(dictionary1,dictionary2)
    k_val_dictionary = dictionary2
    kval_items = k_val_dictionary.items()
    k_val_dictionary = dict(sorted(kval_items))
    return  k_val_dictionary
    

# plotGrid(data2, desired_height, desired_width)

k_val_dictionary = getKValueDictionary(kValueCoords, kVals)
 # Identify every cell's proximity to k0 values
for k0 in k0vals:
    for i in range(len(data2)): # i is grid row
        for j in range(len(data2[0])): # j is grid col in that row
            y, x = i, j
            current_cell_value = data2[y][x]
            

            point1 = np.array((x, y))
            point2 = np.array(k0)
            distanceToKValue = int(np.linalg.norm(point2-point1))
            if data2[y][x] == 0:
                if ((x,y) in k0vals):
                    cellID = 1
                    k_val_dictionary[(x,y)] = cellID
                continue
            if distanceToKValue > max_k0_visble_distance:
                continue
            if distanceToKValue == 0:    
                data2[y][x] = 0
                cellID = 0
                k_val_dictionary[(x,y)] = cellID
                continue
            else:
                cellID = k_val_dictionary[(x,y)] 

                same_kval_factor = 1 / distanceToKValue
                if cellID == 1:
                    data2[y][x] = 1
                    continue
                else:
                    P_same_kval = current_cell_value * (1 - same_kval_factor)
                    data2[y][x] = P_same_kval 
                    cellID = 0
                    k_val_dictionary[(x,y)] = cellID  
# Identify every cell's proximity to k1 values
for k1 in k1vals:
    for i in range(len(data2)): # i is grid row
        for j in range(len(data2)): # j is grid col in that row
            y, x = i, j
            current_cell_value = data2[y][x]
            point1 = np.array((x, y))
            point2 = np.array(k1)
            distanceToKValue = int(np.linalg.norm(point2-point1))
            if data2[y][x] == 0:
                if ((x,y) in k1vals):
                    cellID = 1
                    k_val_dictionary[(x,y)] = cellID
                continue
            if distanceToKValue > max_kval_visble_distance:
                continue
            if distanceToKValue == 0:
                data2[y][x] = 0
                cellID = 1
                k_val_dictionary[(x,y)] = cellID
                continue
            else:
                cellID = k_val_dictionary[(x,y)] 
                same_kval_factor = 1 / distanceToKValue
                if cellID == 0:
                    data2[y][x] = 1
                    continue
                if cellID == 1:
                    data2[y][x] = current_cell_value * (1-(same_kval_factor*same_kval_factor))
                    continue
                else:
                    P_same_kval = current_cell_value * (1 - same_kval_factor)
                    data2[y][x] = P_same_kval
                    cellID = 1
                    k_val_dictionary[(x,y)] = cellID
# print(k_val_dictionary)
 
plotGrid(data, desired_height, desired_width)
plotGrid(data2, desired_height, desired_width)

