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
from shapely.ops import cascaded_union, linemerge
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
                plt.plot(ax, ay, 'ko')
    elif a.geom_type == 'Point':
        b = tuple(a.coords[0])
        if b not in coordinates:
            intpoints[v].append(b)
            qpoints.append(b)
            bbpts.append(b)


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

segmentLines=[]
segmentLinesDict={}
for i in range(len(allpts)-1):    
    pt1 = allpts[i]
    pt2 = allpts[i+1]
    line = (pt1,pt2)
    segmentLines.append(line)
    segmentvalue = segmentvalsdict[pt1]
    if segmentvalue not in segmentLinesDict:
        segmentLinesDict[segmentvalue] = [line]
    else:
        segmentLinesDict[segmentvalue].append(line)
        
        
routerpt = (routerx, routery)
# Determine k region on and within polygon
def getKRegionPolygonLines(kvalue, routerpt, segmentvalsdict, segmentLinesDict, allpts):
    klines=[]
 
    # for key in intpoints.keys():
    #     intersectionpts = intpoints[key]
    #     if len(intersectionpts) > 1:
    #         endofPoly = intersectionpts[len(intersectionpts)-2]
    #     else:
    #         endofPoly = key
    #     klines.append((routerpt,endofPoly))
    
    for key in segmentLinesDict:
        if key == kvalue:
            kvalueSegments = segmentLinesDict[key]
    kvalsegments1, kvalsegments2 =[],[]
    
    for i in range(len(kvalueSegments)):
        if i % 2 == 0:
            kvalsegments1.append(kvalueSegments[i])
        else:
            kvalsegments2.append(kvalueSegments[i])
            
    for segment in kvalueSegments:   
        pt1,pt2 = segment[0], segment[1]
        if pt1 in allpts2:
            klines.append((pt1, routerpt))
        
        if pt2 in allpts2:
            klines.append((pt2, routerpt))
            
        klines.append(segment)
    merge = linemerge(klines)
    
    a = list(merge)
    lines1=[]
    lines2=[]
    i=0
    for line in a:
        if i % 2 == 0:
            lines1.append(line)
        else:
            lines2.append(line)
        i+=1
    # i=0
    # for pt in allpts:
    #     if segmentvalsdict[pt] == kvalue and pt != allpts[len(allpts)-1]:
    #         nextpt = allpts[i+1]
    #         klines.append((pt,nextpt))
    #         for vals in intpoints.values():
    #             if pt in vals:
    #                 if pt != vals[len(vals)-2]:
    #                     klines_secondary.append((routerpt,pt))
    #                     klines_secondary.append((routerpt,nextpt))
    #                     klines_secondary.append((pt,nextpt))
    #             elif nextpt in vals:
    #                 if nextpt != vals[len(vals)-2]:
    #                     klines_secondary.append((routerpt,pt))
    #                     klines_secondary.append((routerpt,nextpt))
    #                     klines_secondary.append((pt,nextpt))    
    #     i+=1
        
     
    return lines1, lines2

# Determine k region along bounding box
def getKRegionBoundingBoxLines(kvalue, routerpt, segmentvalsdict, bbpts, bbpts2):  
    def sortBoundingBoxCCW(boundingboxlist):
        listofpoints = np.array(bbpts2)
        minx,maxx = min(listofpoints[:,0]),max(listofpoints[:,0])
        miny,maxy = min(listofpoints[:,1]),max(listofpoints[:,1])
        new_list = [(maxx,miny),(maxx,maxy),(minx,maxy),(minx,miny)] # y coords are inverted in matplotlib
        return new_list

    boundingboxvertices = sortBoundingBoxCCW(bbpts2)
    
    def getBoundingBoxLines(boundingboxvertices):
        bblines=[]
        for i in range(len(boundingboxvertices)):
            if i != len(boundingboxvertices)-1:
                pt1 = boundingboxvertices[i]
                pt2 = boundingboxvertices[i+1]
                line = [pt1,pt2]
            else:
                pt1 = boundingboxvertices[i]
                pt2 = boundingboxvertices[0]
                line = [pt1,pt2]
            bblines.append(line)
        return bblines
    
    boundingboxlines = getBoundingBoxLines(boundingboxvertices)
    
    def insertBoundingBoxIntersectionPoints(boundingboxlines, bbintpointslist):
        for point in bbintpointslist:
            pointx, pointy = point[0], point[1]
            for line in boundingboxlines:
                if pointy == line[0][1]: # horizontal point
                    if pointx < line[0][0] and pointx > line[len(line)-1][0]:
                        line.insert((len(line)//2), (pointx,pointy))
                    elif pointx > line[0][0] and pointx < line[len(line)-1][0]:
                        line.insert((len(line)//2), (pointx,pointy))
                elif pointx == line[0][0]: # vertical point
                    if pointy > line[0][1] and pointy < line[len(line)-1][1]:
                       line.insert((len(line)//2), (pointx,pointy)) 
                    elif pointy < line[0][1] and pointy > line[len(line)-1][1]:
                       line.insert((len(line)//2), (pointx,pointy)) 
                        
        return boundingboxlines
    boundingboxlines = insertBoundingBoxIntersectionPoints(boundingboxlines, bbpts)
    boundingboxlines_sorted=[]
    for bbline in boundingboxlines:     
        middlepts = bbline[1:len(bbline)-1]
        if len(middlepts) > 1:
            m1x, m1y = middlepts[0][0], middlepts[0][1]
            m2x, m2y = middlepts[1][0], middlepts[1][1]
        if m1x == m2x: #vertical pts
            middlepts.sort()
        elif m1y == m2y:
            middlepts.sort(reverse=True)
        bbline_sorted = [bbline[0]] + middlepts + [bbline[len(bbline)-1]]
        boundingboxlines_sorted.append(bbline_sorted)
        
    # print(boundingboxlines_sorted)
    total_boundingboxpts_sorted = []
    for line in boundingboxlines_sorted:
        for pt in line:
            if pt not in total_boundingboxpts_sorted:
                total_boundingboxpts_sorted.append(pt)
        
            
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
    
    boundingbox_startpts=[]
    for point in total_boundingboxpts_sorted:
        if point in segmentvalsdict.keys() and segmentvalsdict[point] < kvalue:
            boundingbox_startpts.append(point)
           
    def getBoundingBoxPoints(startpt, total_boundingboxpts_sorted, bbpts):
        boundingboxpoints=[]
        startIndex=total_boundingboxpts_sorted.index(startpt)+1
        for i in range(startIndex, len(total_boundingboxpts_sorted)):
            point = total_boundingboxpts_sorted[i]
            if point in bbpts: # break if point is an intersection point
                boundingboxpoints.append(point)
                break
            boundingboxpoints.append(point)
        return boundingboxpoints
    
    kBoundingBoxLines = []
    for startpt in boundingbox_startpts:
        linepts = getBoundingBoxPoints(startpt, total_boundingboxpts_sorted, bbpts)
        linepts.insert(0,startpt)
        kBoundingBoxLines.append(linepts)
     
    def completeBoundingBoxLines(startpt, kvalue, segmentvalsdict, total_boundingboxpts_sorted):
        startIndex = total_boundingboxpts_sorted.index(startpt)
        reshuffledBBPts_end = total_boundingboxpts_sorted[startIndex:]
        reshuffledBBPts_start = total_boundingboxpts_sorted[0:startIndex]
        reshuffledBBPts = reshuffledBBPts_end + reshuffledBBPts_start
        continuedBBPts = []
        for pt in reshuffledBBPts:
            continuedBBPts.append(pt)
            if pt in segmentvalsdict.keys() and segmentvalsdict[pt] >=kvalue:
                return continuedBBPts
                
    newBBLines=[]
    for line in kBoundingBoxLines:
        if line[-1] in boundingboxvertices:
            continuedBBPoints = completeBoundingBoxLines(line[-1], kvalue, segmentvalsdict, total_boundingboxpts_sorted)
            continuedBBLines = makeLinesFromPointsList(continuedBBPoints)
            for line2 in continuedBBLines:
                newBBLines.append(line2)
    for line in newBBLines:
        kBoundingBoxLines.append(line)
    
    for pt in bbpts:
        if segmentvalsdict[pt] <=kvalue:
            line = (routerpt, pt)
            kBoundingBoxLines.append(line)
    print(kBoundingBoxLines)
    return kBoundingBoxLines   

def getKRegion(kvalue, routerpt, segmentvalsdict, segmentLinesDict, allpts, allpts2, bbpts, bbpts2):
    ax = plt.gca()
   
    klines, klines_secondary = getKRegionPolygonLines(kvalue, routerpt, segmentvalsdict, segmentLinesDict, allpts)
    kBoundingBoxLines = getKRegionBoundingBoxLines(kvalue,  routerpt, segmentvalsdict, bbpts, bbpts2)
    kregion = list(polygonize(klines))
    kregion2 = list(polygonize(klines_secondary))
    kregion3 = list(polygonize(kBoundingBoxLines))
    total_polygons = [polygon for polygon in kregion] + [polygon for polygon in kregion2]+ [polygon for polygon in kregion3]
    polygon_final = cascaded_union(total_polygons)

    k2fill = PolygonPatch(polygon_final,facecolor='#cccccc', edgecolor='None')
    ax.add_patch(k2fill)
    plt.xlim(50, 908)
    plt.ylim(-697, 15)
    plt.show()
            



getKRegion(2, routerpt, segmentvalsdict, segmentLinesDict, allpts, allpts2, bbpts, bbpts2)
