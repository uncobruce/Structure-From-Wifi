import matplotlib.pyplot as plt
from shapely.geometry import  Point, Polygon, LineString, GeometryCollection
import numpy as np
import cv2
import math
from bresenham import bresenham

# Create list of points from given vertices
verticesArray = ([462., 636.], [434., 416.], [599., 382.],[424., 277.],   
                    [709., 197.], [702., 384.], [850., 496.], [877.,  23.],
                    [454.,  14.], [189.,  85.], [ 85., 257.],
                    [100., 474.], [227., 443.], [217., 264.], [351., 264.], [324., 529.],
                    [211., 621.])
verticesArray = list(verticesArray)
# verticesArray.reverse()
points = []
for v in verticesArray:
    px, py = v[0], -v[1]
    p = (px,py)
    points.append(p)

# Define router position
routerx, routery = 400, -570

# Create polygon from vertices and plot
poly = Polygon(points)
coordinates = list(poly.exterior.coords)
plt.plot(*poly.exterior.xy)

for point in coordinates:
    px, py = point[0], point[1]
    plt.plot(px, py, 'bo')    
    
# STEP 1) Find and plot critical vertices
# -------------------------------------------------------------------------
def isVertexCritical(criticalRay, p1, p2):
    # criticalRay: LineString object giving critical ray
    # return True if vertex is critical vertex 
    router = criticalRay.coords[0]
    vi = criticalRay.coords[1]
    routerx, routery = router[0], router[1]
    line = {'x1': routerx,'y1':-routery,'x2':vi[0],'y2':-vi[1]}
    p1 = {'x':p1[0],'y':-p1[1]}
    p2 = {'x':p2[0],'y':-p2[1]} 
    return ((line['y1'] - line['y2'])*(p1['x'] - line['x1'])+(line['x2']- line['x1'])*(p1['y']-line['y1']))*((line['y1']-line['y2'])*(p2['x']-line['x1'])+(line['x2']-line['x1'])*(p2['y']-line['y1']))>0

routerPoint = Point((routerx, routery))
i=0
criticalvertices=[]
for coord in coordinates:
    coord2 = (coord[0] + 100, coord[1]+100)
    rc = LineString([routerPoint, coord])
    if i!=0 and i!= len(coordinates)-1:
        if isVertexCritical(rc, coordinates[i-1], coordinates[i+1]):
            criticalvertices.append(coord)
            plt.plot(*rc.xy, 'k--',linewidth=2.0,)
            plt.plot(coord[0],coord[1],'ro')
            
    i+=1
plt.plot(routerx, routery, 'go') # plot router point   


# STEP 2) Checking ray-poly intersections
# -------------------------------------------------------------------------
def extendRay(routerPoint, vertex):
    x1, y1 = routerPoint.x, routerPoint.y
    x2, y2 = vertex[0], vertex[1]
    extendLength = 1000
    diff = (x2-x1, y2-y1)
    mag = math.sqrt((x2-x1)**2 + (y2-y1)**2)
    norm = (diff[0] / mag, diff[1]/mag) 
    p3 = (vertex[0] + extendLength*norm[0],vertex[1] + extendLength*norm[1])
    x3,y3 = p3[0], p3[1]
    return (x3,y3)

# Get intersection points
intpoints = {}
qpoints = []
for v in criticalvertices:
    rc = LineString([routerPoint, v])
    v2 = extendRay(routerPoint, v)
    rc2 = LineString([v, v2])
    a = poly.exterior.intersection(rc2)
    plt.plot(*rc2.xy, 'k--',linewidth=2.0,)
    intpoints[v] = []
    if a.geom_type == 'MultiPoint':
        for i in range(len(a)):
            b = tuple(a.bounds)
            ax, ay = a[i].x, a[i].y
            coord = (ax, ay)
            if coord not in coordinates:
                intpoints[v].append(coord)
                qpoints.append(coord)
            #     if v not in intpoints: intpoints[v] = coord
            #     else:
            #         intpoints[v].extend(coord)
                plt.plot(ax, ay, 'ko')
    elif a.geom_type == 'Point':
        b = tuple(a.coords[0])
        if b not in coordinates:
            intpoints[v].append(b)
            qpoints.append(b)
            plt.plot(*a.coords.xy[0], *a.coords.xy[1], 'ko')

# +1/-1 rule
def isLeftTurn(vi, viPrev, viNext):
    # given a vertex, determine if CW or CCW
    # returns True if CCW (left turn), returns False if CW (right turn)
    return ((vi[0] - viPrev[0])*(viNext[1]-vi[1]) - (vi[1]-viPrev[1])*(viNext[0]-vi[0]) > 0  )

def onPositiveSide(vi, viPrev, routerx, routery):
    # given a vertex, determine if vPrev is on positive side of the ray 
    # ray is defined as line connecting transmitter coords to vi coords
    line = {'x1': routerx,'y1':routery,'x2':vi[0],'y2':vi[1]}
    p1 = {'x':viPrev[0],'y':viPrev[1]}
    return (( (line['y1'] - line['y2'])*(p1['x'] - line['x1'])+(line['x2']- line['x1'])*(p1['y']-line['y1']) )>0)
i=0
pointIDs={} 
for v in coordinates:
     if i!= len(coordinates) and v in criticalvertices:
         vprev = coordinates[i-1]
         vnext = coordinates[i+1]
         if isLeftTurn(v, vprev, vnext):
             if onPositiveSide(v, vprev, routerx, routery):
                 pointIDs[v] = 1
             else:
                 pointIDs[v] = -1
         else:
             if onPositiveSide(v, vprev, routerx, routery):
                 pointIDs[v] = -1
             else:
                 pointIDs[v] = 1
     i+=1
                
# +2/-2 rule
def get_v_j_prev(coordinates, q):
    i=0
    for coord in coordinates:
        if i != len(coordinates)-1:
            pt1 = np.array(coord)
            pt2 = np.array(coordinates[i-1])
            pt3 = np.array(q)
            d12 = int(np.linalg.norm(pt2-pt1))
            d13 = int(np.linalg.norm(pt3-pt1))
            d23 = int(np.linalg.norm(pt2-pt3))
            if d12-1 == d13 + d23 or d12 == d13 + d23:
                return tuple(pt2)
        i+=1
    


def onSameSide(criticalRay, p1, p2):
    # criticalRay: LineString object giving critical ray
    # return True if v_i_prev and v_j_prev are on same side
    router = criticalRay.coords[0]
    vi = criticalRay.coords[1]
    routerx, routery = router[0], router[1]
    line = {'x1': routerx,'y1':-routery,'x2':vi[0],'y2':-vi[1]}
    p1 = {'x':p1[0],'y':-p1[1]}
    p2 = {'x':p2[0],'y':-p2[1]} 
    return ((line['y1'] - line['y2'])*(p1['x'] - line['x1'])+(line['x2']- line['x1'])*(p1['y']-line['y1']))*((line['y1']-line['y2'])*(p2['x']-line['x1'])+(line['x2']-line['x1'])*(p2['y']-line['y1']))>0
i=0
for v in coordinates:
    if i!= 0 and v in criticalvertices: 
        v_i_prev = coordinates[i-1]
        qpts = intpoints[v] # list of intersection points for critical ray
        if qpts is not []:
            for q in qpts:
                v_j_prev = get_v_j_prev(coordinates, q)
                v2 = extendRay(routerPoint, v)
                rc = LineString([routerPoint, v2])
                if onSameSide(rc, v_j_prev, v_i_prev):
                    pointIDs[q] = -2
                else:
                    pointIDs[q] = 2
    i+=1

# Step 2c - labelling edge segments
def insertQ(allpts, q):
    i=0
    allpts2=allpts.copy()
    for p in allpts2:
       if i != len(allpts2)-1: 
           p1 = np.array(p)
           p2 = np.array(allpts[i+1])
           p3 = np.array(q)
           d12 = int(np.linalg.norm(p2-p1))
           d13 = int(np.linalg.norm(p3-p1))
           d23 = int(np.linalg.norm(p2-p3))
           if d12-1 == d13 + d23 or d12 == d13 + d23:
               allpts.insert(i+1, tuple(p3))
       i+=1

    return allpts

allpts = coordinates.copy()
# Create list of all crit vertices and intersection pts, in ccw order around poly
for q in qpoints:
    allpts = insertQ(allpts,q)
    
allpts2=[]
for pt in allpts:
    if pt in criticalvertices:
        allpts2.append(pt)
    elif pt in qpoints:
        allpts2.append(pt)
    
allpts = allpts2
# allpts.reverse()

# Get coords of point z and plot, insert into allpts
temp_pt = (routerx+100, routery)
temp_ray = LineString([routerPoint, temp_pt])
horiz_int = poly.exterior.intersection(temp_ray)
zx, zy = horiz_int.x, horiz_int.y
z = (zx, zy)
plt.plot(zx,zy,'mo')
allpts.insert(0, z)

# Obtain edge segment vals
polyvalue=0
segmentvals = []
for pt in allpts:
    if pt == allpts[0]:
        polyvalue=0
        segmentvals.append(polyvalue) #keep track of segment "ahead" of pt
    else:
        ptID = pointIDs[pt]
        polyvalue = polyvalue + ptID
        segmentvals.append(polyvalue)
       
# Show final result
plt.xlim(50, 900)
plt.ylim(-700, 0)
plt.show()
