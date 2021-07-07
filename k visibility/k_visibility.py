import matplotlib.pyplot as plt
from shapely.geometry import  Point, Polygon, LineString, GeometryCollection
import numpy as np
import cv2
import math
from bresenham import bresenham
import sys
from shapely.ops import polygonize, polygonize_full
from descartes import PolygonPatch
from matplotlib.collections import PatchCollection
from shapely.ops import cascaded_union
from matplotlib.path import Path
import matplotlib.patches as patches
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


# Get coords of point z and plot, insert into allpts
temp_pt = (routerx+100, routery)
temp_ray = LineString([routerPoint, temp_pt])
horiz_int = poly.exterior.intersection(temp_ray)
zx, zy = horiz_int.x, horiz_int.y
z = (zx, zy)
plt.plot(zx,zy,'mo')
allpts2.insert(0, z)
allpts.insert(0, z)
pointIDs[z] = 1000
# Obtain edge segment vals
polyvalue=0
segmentvals = []
for pt in allpts2:
    if pt == allpts2[0]:
        polyvalue=0
        segmentvals.append(polyvalue) #keep track of segment "ahead" of pt
    else:
        ptID = pointIDs[pt]
        polyvalue = polyvalue + ptID
        segmentvals.append(polyvalue)
        

# STEP 3) Constructing k-visibility regions
# -------------------------------------------------------------------------
# Plot the bounding box
bbpts = []
bbpts2 =[]
p1 = Point(55, -695)
p2 = Point(55, 10)
p3 = Point(905, 10)
p4 = Point(905, -695)
points = (p4,p3,p2,p1)
boundingbox = Polygon(points)
for pt in points:
    ptx, pty = pt.x, pt.y
    # bbpts.append((ptx,pty))
    bbpts2.append((ptx,pty))
      
# Add bounding box intersections to intpoints
for v in criticalvertices:
    rc = LineString([routerPoint, v])
    v2 = extendRay(routerPoint, v)
    rc2 = LineString([v, v2])
    a = boundingbox.exterior.intersection(rc2)
    if a.geom_type == 'MultiPoint':
        for i in range(len(a)):
            b = tuple(a.bounds)
            ax, ay = a[i].x, a[i].y
            coord = (ax, ay)
            if coord not in coordinates:
                intpoints[v].append(coord)
                qpoints.append(coord)
                bbpts.append(coord)
                bbpts2.append(coord)
                plt.plot(ax, ay, 'ko')
    elif a.geom_type == 'Point':
        b = tuple(a.coords[0])
        if b not in coordinates:
            intpoints[v].append(b)
            qpoints.append(b)
            bbpts.append(b)
            bbpts2.append(b)

            plt.plot(*a.coords.xy[0], *a.coords.xy[1], 'ko')


# Represent all coords by their next segment vals
segmentvalsdict = {}
for i in range(len(allpts2)):
    point = allpts2[i]
    segmentvalsdict[point] = segmentvals[i]
    
currentsegval = None
for coord in allpts:
    if coord in allpts2:
        currentsegval = segmentvalsdict[coord]
    else:
        segmentvalsdict[coord] = currentsegval
        
for point in bbpts:
    for val_list in intpoints.values():
        if point in val_list:
            pointIndex = val_list.index(point)
            if pointIndex > 0:
                pointIndex-=1
                beforept = val_list[pointIndex]
            elif pointIndex == 0:
                for key in intpoints.keys():
                    if intpoints[key] == val_list:
                        beforept = key
    beforept_segval = segmentvalsdict[beforept]
    segmentvalsdict[point] = beforept_segval
    pointIDs[point] = 2
ax = plt.gca()
k2lines=[]
k2linestrings = []
for vertex in criticalvertices:
    if segmentvalsdict[vertex] <= 2:
        rc = LineString([routerPoint, vertex])
        k2lines.append(((routerx,routery),vertex))
        k2linestrings.append(rc)

     

i=0
for pt in allpts:
    if segmentvalsdict[pt] == 2 and pt != allpts[len(allpts)-1]:
        nextpt = allpts[i+1]
        rc = LineString([pt, nextpt])
        # plt.plot(*rc.xy, 'k',linewidth=2.0,)
        k2lines.append((pt,nextpt))
        k2lines.append(((routerx,routery),nextpt))
        k2lines.append((pt,(routerx,routery)))
        k2linestrings.append(rc)
        # for qlist in intpoints.values():
        #     if pt in qlist:
        #         ptindex = qlist.index(pt)
        #         nextpt2 = (routerx,routery)
        #         k2lines.append((pt,nextpt2))
        #         rc = LineString([pt, nextpt])
        #         plt.plot(*rc.xy, 'k',linewidth=2.0,)
    i+=1
for critvertex in intpoints.keys():
    intersectionpts = intpoints[critvertex]
    for pt in intersectionpts:
        if pt not in bbpts:
            ptPolyIndex = allpts.index(pt)
            prevPoint = allpts[ptPolyIndex-1]
            nextPoint = allpts[ptPolyIndex+1]
        if segmentvalsdict[pt] <= 2:

            endpt = pt
            rc = LineString([critvertex, endpt])
            # plt.plot(*rc.xy, 'k',linewidth=2.0,)
            k2linestrings.append(rc)
            k2lines.append((critvertex,endpt))
            if pt == intersectionpts[len(intersectionpts)-2] and segmentvalsdict[prevPoint] > 2:
                endpt = pt
                rc = LineString([critvertex, endpt])
                k2lines.append((critvertex,endpt))
                k2linestrings.append(rc)
                break
            if pt not in bbpts and segmentvalsdict[pt] < 2 and segmentvalsdict[prevPoint] == 2:
                endpt1 = pt
                endpt2 = intersectionpts[len(intersectionpts)-1]
                k2lines.append((endpt1,endpt2))

        elif pt not in bbpts and segmentvalsdict[prevPoint] == 2:
            endpt = pt
            rc = LineString([critvertex, endpt])
            k2linestrings.append(rc)
            k2lines.append((critvertex,endpt))
            break   
lines = []
bbpts.sort()
for i in range(len(bbpts)-1):
    pt1 = (bbpts[i][0], bbpts[i][1])
    pt2 = (bbpts[i+1][0], bbpts[i+1][1])
    
k2lines.append((((447.5085324232082, 10.0)),((307.124183006536, 10.0))))
bb1 = LineString([(447.5085324232082, 10.0), (307.124183006536, 10.0)])
# plt.plot(*bb1.xy, 'k',linewidth=2.0,)
k2linestrings.append(bb1)
k2lines.append((((55.0, -459.6)),(55,-695)))
bb2 = LineString([(55.0, -459.6), (55,-695)])
# plt.plot(*bb2.xy, 'k',linewidth=2.0,)
k2linestrings.append(bb2)
k2lines.append((((905,-695)),(55,-695)))
bb3 = LineString([(905,-695), (55,-695)])
# plt.plot(*bb3.xy, 'k',linewidth=2.0,)
k2linestrings.append(bb3)
k2lines.append((((905,-695)),(905.0, -486.9555555555556)))
bb4 = LineString([(905,-695), (905.0, -486.9555555555556)])
k2linestrings.append(bb4)
# plt.plot(*bb4.xy, 'k',linewidth=2.0,)


k2region = list(polygonize(k2lines))
polygons = [polygon for polygon in k2region]
new_pol = cascaded_union(polygons) 
polygon2, dangles, cuts, invalids = polygonize_full(k2lines)
k2fill = PolygonPatch(new_pol,facecolor='#cccccc', edgecolor='#999999')
ax.add_patch(k2fill)


# Show final result
plt.xlim(50, 908)
plt.ylim(-697, 15)
plt.show()
