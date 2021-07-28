import matplotlib.pyplot as plt
import vertices2
from shapely.geometry import  Point, Polygon, LineString, MultiLineString
import numpy as np
import math
from shapely.ops import polygonize
from descartes import PolygonPatch
from shapely.ops import cascaded_union
import random
import cv2
# Create list of points from given vertices
with open("mapEdges.txt") as f:
    content = f.readlines() 
f.close()
content = [x.strip() for x in content] 
fig = plt.figure()

# Define floor map and plot
contour = np.squeeze(vertices2.contours[0])
poly = Polygon(contour)
plt.plot(*poly.exterior.xy, 'k',linewidth=2.0)


# Define plot x limits and y limits
coordinates = list(poly.exterior.coords)
coords2 = np.array(coordinates)
xcoords, ycoords = coords2[:,0], coords2[:,1]
xmin, xmax = min(xcoords), max(xcoords)
ymin, ymax = min(ycoords), max(ycoords)
plt.xlim(xmin - 100, xmax + 100)
plt.ylim(ymin - 100, ymax+100)

# Define bounding box poly
bbox = Polygon([(xmin-100, ymin-100), (xmax+100, ymin-100), (xmax+100, ymax+100), (xmin-100, ymax+100)])
plt.plot(*bbox.exterior.xy, 'k')

# Obtain a router point at a randomly placed location
routerPoint = poly.representative_point()
routerx, routery = routerPoint.x, routerPoint.y-200
routerPoint = Point(routerx, routery)
routerpt = (routerx,routery)
for point in coordinates:
    px, py = point[0], point[1]
plt.plot(routerx,routery, 'ko')


# Count intersections for rays drawn to each vertex
vertexIntersections={}
eps = 50
for point in coordinates:
    rc = LineString([routerPoint, point])
    # plt.plot(*rc.xy, 'b', linewidth=0.75)
    if rc.intersects(poly):
        intersection = rc.intersection(poly)
        if intersection.geom_type == 'MultiLineString':
            numIntersections=0
            for linestring in intersection:
                if linestring == intersection[0]:
                    continue
                elif linestring == intersection[-1]:
                    endpoint = linestring.coords[0]
                    endpt = np.array(endpoint)
                    compare = np.array(point)
                    distance = int(np.linalg.norm(compare-endpt))
                    if distance < 5:
                            numIntersections+=1 # ensure intersections are not the actual endpoint
                    else:
                        numIntersections+=2
                else:
                    numIntersections+=2
            if point not in vertexIntersections:
                vertexIntersections[point] = numIntersections
        elif intersection.geom_type == 'LineString':
            numIntersections=0
            if point not in vertexIntersections:
                vertexIntersections[point] = numIntersections
        elif intersection.geom_type == 'GeometryCollection':
            numIntersections=0
            for geometry in intersection:
                if geometry.geom_type == 'Point':
                    continue
                elif geometry.geom_type == 'LineString':
                    if geometry.coords[0] == routerpt:
                        numIntersections+=1 # only count intersection on end of this ray
                    elif geometry == intersection[-1]:
                        endpoint = geometry.coords[1]
                        endpt = np.array(endpoint)
                        compare = np.array(point)
                        distance = int(np.linalg.norm(compare-endpt))
                        if distance < 5:
                            numIntersections+=1 # ensure intersections are not the actual endpoint
                        else:
                            numIntersections+=2
                    else:
                        numIntersections +=2 # intersections for every other linestring count for 2     
            compare = intersection[len(intersection)-1]
            comparept = np.array(compare.coords[1])
            pt = np.array(point)
            distance = int(np.linalg.norm(pt-comparept))
            if point not in vertexIntersections:
                vertexIntersections[point] = numIntersections
            
            
            
# Extend vertices to obtain intersection points and record intersections
def extendRay(routerPoint, vertex):
    # Return coordinate of extended ray
    x1, y1 = routerPoint.x, routerPoint.y
    x2, y2 = vertex[0], vertex[1]
    extendLength = 1000
    diff = (x2-x1, y2-y1)
    mag = math.sqrt((x2-x1)**2 + (y2-y1)**2)
    norm = (diff[0] / mag, diff[1]/mag) 
    p3 = (vertex[0] + extendLength*norm[0],vertex[1] + extendLength*norm[1])
    x3,y3 = p3[0], p3[1]
    return (x3,y3)

def removeClosePoints(points):
    points2 = points.copy()
    for i in range(len(points2)-1):
        p1 = np.array(points2[i])
        p2 = np.array(points2[i+1])
        distance = np.linalg.norm(p2-p1)
        if distance < 5:
            points.remove(points2[i])
    return points


qIntersections={}
for coord in coordinates:
    extendedpoint = extendRay(routerPoint, coord)
    extendedray = LineString([routerPoint, extendedpoint])
    # plt.plot(*extendedray.xy,'k', linewidth=0.25)
    if extendedray.intersects(poly):
        intersection = extendedray.intersection(poly)
        if intersection.geom_type == 'LineString':
            numIntersections=0
            intersectionpt = intersection.coords[1]
            intersectionpt = (int(intersectionpt[0]), int(intersectionpt[1]))
            if intersectionpt not in qIntersections.keys():
                qIntersections[intersectionpt] = numIntersections
        elif intersection.geom_type == 'GeometryCollection':
            numIntersections=0
            intersectionpt = (int(intersection[-1].coords[1][0]), int(intersection[-1].coords[1][1]))
            for geometry in intersection:
                if geometry.geom_type == 'Point':
                    continue
                elif geometry.geom_type == 'LineString':
                    if geometry.coords[0] == routerpt:
                        numIntersections+=1 # only count intersection on end of this ray
                    elif geometry == intersection[-1]:
                        endpt = np.array(intersectionpt)
                        compare = np.array(coord)
                        distance = int(np.linalg.norm(compare-endpt))
                        if distance < 10:
                            numIntersections+=1 # ensure intersections are not the actual endpoint
                        else:
                            numIntersections+=2
                    else:
                        numIntersections +=2 
            compare = intersection[len(intersection)-1]
            comparept = np.array(compare.coords[1])
            pt = np.array(point)
            distance = int(np.linalg.norm(pt-comparept))
            if intersectionpt not in qIntersections.keys():
                qIntersections[intersectionpt] = numIntersections
        elif intersection.geom_type == 'MultiLineString':
            intersectionpt = (int(intersection[-1].coords[1][0]), int(intersection[-1].coords[1][1]))
            
            numIntersections=0
            pointsCrossed=[]
            for linestring in intersection:
                p1, p2 = linestring.coords[0], linestring.coords[1]
                if p1 == routerpt:
                    continue
                if ((int(p1[0]), int(p1[1]))) not in pointsCrossed:
                    pointsCrossed.append(((int(p1[0]), int(p1[1]))))
                    numIntersections+=1
                                     
                if ((int(p2[0]), int(p2[1]))) not in pointsCrossed:
                    pointsCrossed.append(((int(p2[0]), int(p2[1]))))
                    numIntersections+=1
                if linestring == intersection[-1]:
                    endpoint = linestring.coords[1]
                    endpt = np.array(endpoint)
                    compare = np.array(point)
                    distance = int(np.linalg.norm(compare-endpt))
                    if distance < 5:
                        pointsCrossed.append(((int(p2[0]), int(p2[1]))))
                        numIntersections+=1 # ensure intersections are not the actual endpoint
            pointsCrossed = removeClosePoints(pointsCrossed)
            numIntersections = len(pointsCrossed)
            if intersectionpt not in qIntersections.keys():
                qIntersections[intersectionpt] = numIntersections

qpoints = list(qIntersections.keys())



bboxcoords = [(xmin-100, ymin-100), (xmax+100, ymin-100), (xmax+100, ymax+100), (xmin-100, ymax+100)]
# Insert q points into coordinates list
def insertQ(coordinates, q):
    i=0
    coordinates2=coordinates.copy()
    for p in coordinates2:
        if i != len(coordinates2)-1: 
            p1 = np.array(p)
            p2 = np.array(coordinates[i+1])
            p3 = np.array(q)
            d12 = int(np.linalg.norm(p2-p1))
            d13 = int(np.linalg.norm(p3-p1))
            d23 = int(np.linalg.norm(p2-p3))
            if d12-1 == d13 + d23 or d12 == d13 + d23:
                if np.linalg.norm(p3-p2) > 5:
                    coordinates.insert(i+1, tuple(p3))
                    break
        i+=1   





    
offsetIntersections={}
# Plot offset rays for every qpoint to ensure points behind vertices are seen for k0 regions
for q in qpoints:
    angle = math.atan(q[1]/q[0])
    angleoffset = -0.2
    xoffset = (q[0]*math.cos(angleoffset)) - (q[1]*math.sin(angleoffset))
    yoffset = (q[0]*math.sin(angleoffset)) + (q[1]*math.cos(angleoffset))
    extendedoffsetpt = extendRay(routerPoint, (xoffset,yoffset))
    rayoffset = LineString([routerpt, extendedoffsetpt])
    intersection = rayoffset.intersection(poly)
    if intersection.geom_type == 'MultiLineString':
        pass
    else:
        intersectionpt = (int(intersection.coords[1][0]), int(intersection.coords[1][1]))
        numIntersections=0
        if intersectionpt not in offsetIntersections.keys():
            offsetIntersections[intersectionpt] = numIntersections
            # plt.plot(*rayoffset.xy, 'r', linewidth = 0.4)
for q in qpoints:
    angle = math.atan(q[1]/q[0])
    angleoffset = 0.2
    xoffset = (q[0]*math.cos(angleoffset)) - (q[1]*math.sin(angleoffset))
    yoffset = (q[0]*math.sin(angleoffset)) + (q[1]*math.cos(angleoffset))
    extendedoffsetpt = extendRay(routerPoint, (xoffset,yoffset))
    rayoffset = LineString([routerpt, extendedoffsetpt])
    intersection = rayoffset.intersection(poly)
    if intersection.geom_type == 'MultiLineString':
        pass
    else:
        intersectionpt = (int(intersection.coords[1][0]), int(intersection.coords[1][1]))
        numIntersections=0
        if intersectionpt not in offsetIntersections.keys():
            offsetIntersections[intersectionpt] = numIntersections
            # plt.plot(*rayoffset.xy, 'r', linewidth = 0.4)
offsetpts = list(offsetIntersections.keys())

# coordinates=removeClosePoints(coordinates)
# offsetpts = removeClosePoints(offsetpts)
# qpoints = removeClosePoints(qpoints)

for q in qpoints:
    insertQ(coordinates, q)
for o in offsetpts:
    insertQ(coordinates, o)

# Remove any duplicates/near-duplicates from new coordinates list
coordinates = list(dict.fromkeys(coordinates))
coordinates = removeClosePoints(coordinates)

def getPointValue(point, vertexIntersections, qIntersections):
    segval = None
    if point in vertexIntersections.keys():
        segval = vertexIntersections[point]
        return segval
    elif point in qIntersections.keys():
        segval = qIntersections[point]
        return segval
    elif point in offsetIntersections.keys():
        segval = offsetIntersections[point]
        return segval
  
    return segval

bboxintersections = {}
for pt in coordinates:
    extendedpoint = extendRay(routerPoint, pt)
    extendedray = LineString([routerPoint, extendedpoint])
    numIntersectionstoPoly = getPointValue(pt, vertexIntersections, qIntersections)
    bboxnumIntersections = numIntersectionstoPoly+1
    if extendedray.intersects(bbox):
        intersection = extendedray.intersection(bbox)
        intersectionpt = intersection.coords[1]
        bboxintersections[intersectionpt] = bboxnumIntersections
        
bboxintersectionpts = list(bboxintersections.keys())


# bboxcoords = list(dict.fromkeys(bboxcoords))
# bboxcoords =  removeClosePoints(bboxcoords)
pointValuesDict={}
for coord in coordinates:
    pointval = getPointValue(coord, vertexIntersections, qIntersections)
    if coord not in pointValuesDict:
        pointValuesDict[coord] = pointval
for pt in bboxintersectionpts:
    insertQ(bboxcoords, pt)


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



        
bboxpointvaluesdict={}
for coord in bboxcoords:
    if coord in bboxintersections:
        pointval = bboxintersections[coord]+1
    bboxpointvaluesdict[coord] = pointval
        
polysegments = makeLinesFromPointsList(coordinates)
bboxsegments = makeLinesFromPointsList(bboxcoords)

finalSegmentLinesDict={}     
for seg in polysegments:
    segval = pointValuesDict[seg[0]]
    segval2 = pointValuesDict[seg[1]]
    if segval not in finalSegmentLinesDict:
        finalSegmentLinesDict[segval] = [seg]
    else:
        finalSegmentLinesDict[segval].append(seg)
    if segval2 not in finalSegmentLinesDict:
        finalSegmentLinesDict[segval2] = [seg]
    else:
        finalSegmentLinesDict[segval2].append(seg)

bboxsegmentlinesdict = {}
for seg in bboxsegments:
    segval = bboxpointvaluesdict[seg[0]]
    segval2 = bboxpointvaluesdict[seg[1]]
    
    if segval not in bboxsegmentlinesdict:
        bboxsegmentlinesdict[segval] = [seg]
    else:
        bboxsegmentlinesdict[segval].append(seg)

        
# Connect segments between vertices for desired k value          
def getKRegionVertexLines(kvalue, coordinates, pointValuesDict, finalSegmentLinesDict,routerpt):   
    kvaluesegments=[]
    for key in finalSegmentLinesDict:
        if key <= kvalue:
            kvaluesegments = kvaluesegments + finalSegmentLinesDict[key]
    totalpolygons = []
    for segment in kvaluesegments:
        p1,p2 = segment[0], segment[1]
        line1 = (p1,p2)
        line2 = (p1, routerpt)
        line3 = (p2, routerpt)
        region = list(polygonize((line1,line2, line3)))
        poly = region[0]
        totalpolygons.append(poly)
    return totalpolygons      

def getBBoxRegionVertexLines(kvalue, bboxcoords, bboxpointvaluesdict, bboxsegmentlinesdict, routerpt):
    kvaluesegments=[]
    for key in bboxsegmentlinesdict:
        if key <= kvalue:
            kvaluesegments = kvaluesegments + bboxsegmentlinesdict[key]
    totalpolygons = []
    for segment in kvaluesegments:
        p1,p2 = segment[0], segment[1]
        line1 = (p1,p2)
        line2 = (p1, routerpt)
        line3 = (p2, routerpt)
        region = list(polygonize((line1,line2, line3)))
        poly = region[0]
        totalpolygons.append(poly)
    return totalpolygons      

# Due to the double wall effect in the polygon contour, every even k point counts as a consecutive k region
# Except for k=0 and k=1, every "k" region desired is actually plotted as the 2k+1 region to compensate
def getKRegion(kvalueinput, coordinates, pointValuesDict, finalSegmentLinesDict,routerpt,facecolor):
    if kvalueinput == 0:
        kvalue = 0
    # elif kvalueinput % 2 != 0:
    #     kvalue = kvalueinput*2
    else:
        kvalue = kvalueinput*2+1   
    kregion = getKRegionVertexLines(kvalue, coordinates, pointValuesDict, finalSegmentLinesDict,routerpt)
    kregionpolys = [poly for poly in kregion]
    polygon_final = cascaded_union(kregionpolys)
    return polygon_final

def getBBoxKRegion(kvalueinput, bboxcoords, bboxpointvaluesdict, bboxsegmentlinesdict, routerpt):
    if kvalueinput == 0:
        kvalue = 0
    # elif kvalueinput % 2 != 0:
    #     kvalue = kvalueinput*2
    else:
        kvalue = kvalueinput*2
    kregion = getBBoxRegionVertexLines(kvalue, bboxcoords, bboxpointvaluesdict, bboxsegmentlinesdict, routerpt)
    kregionpolys = [poly for poly in kregion]
    polygon_final = cascaded_union(kregionpolys)
    return polygon_final

facecolors = ['red','yellow','blue','green']
kvalues = max(np.array(list(pointValuesDict.values()))) // 2
kvaluesdict={}
for i in range(kvalues, -1, -1):
    kvaluesdict[facecolors[i]] = i


ax=plt.gca() 
for i in range(kvalues, 0, -1):
    kregion = getBBoxKRegion(i, bboxcoords, bboxpointvaluesdict, bboxsegmentlinesdict, routerpt)
    kfill = PolygonPatch(kregion, facecolor=facecolors[i], edgecolor='None')
    ax.add_patch(kfill)

kvalpolys = []
for i in range(kvalues, -1, -1):
    kregion = getKRegion(i, coordinates, pointValuesDict, finalSegmentLinesDict, routerpt,facecolors[i])
    kvalpolys.append(kregion)
    kfill = PolygonPatch(kregion, facecolor=facecolors[i], edgecolor='None')
    ax.add_patch(kfill)
kvalpolys.reverse()



plt.show()
# -------------------------------------------------------------------------------------------
plt.plot(*poly.exterior.xy, 'k',linewidth=2.0)
plt.plot(routerx,routery, 'ro')

def obtainRandomTrajectory(xmax, ymax,routerPoint,poly):
    def getStartPoint():
        while True:
            x = random.randrange(xmax)
            y = random.randrange(ymax)
            point = Point(x,y)
            if poly.contains(point) and (not point.intersects(routerPoint)):
                return point
    def getOpenandClosedPositions(currentStep):
        step = 30
        openPositions, openPositionsDict,closedPositions = [], {}, []
        up = Point(currentStep.x, currentStep.y+step)
        down = Point(currentStep.x, currentStep.y-step)
        left = Point(currentStep.x-step, currentStep.y)
        right = Point(currentStep.x+step, currentStep.y)
        
        
        if not (up.intersects(poly.exterior) or not up.within(poly)):
            up = Point(currentStep.x, currentStep.y+(step/10))
            openPositions.append(up)
            openPositionsDict[(up.x,up.y)] = 'up'
        else:
            closedPositions.append(up)
            
        if not (down.intersects(poly.exterior) or not down.within(poly)):
            down = Point(currentStep.x, currentStep.y-(step/10))
            openPositions.append(down)
            openPositionsDict[(down.x, down.y)] = 'down'
        else:
            closedPositions.append(down)  
            
        if not (left.intersects(poly.exterior) or not left.within(poly)):
            left = Point(currentStep.x-(step/10), currentStep.y)
            openPositions.append(left)
            openPositionsDict[(left.x, left.y)] = 'left'
        else:
            closedPositions.append(left)
            
        if not (right.intersects(poly.exterior) or not right.within(poly)):
            right = Point(currentStep.x+(step/10), currentStep.y)
            openPositions.append(right)
            openPositionsDict[(right.x, right.y)] = 'right'
        else:
            closedPositions.append(right)
            
        return openPositions, openPositionsDict, closedPositions
        
    startPoint = getStartPoint()
    currentStep = startPoint
    path = []
    i=0
    limit = 5000
    currentDirection = None
    while i < limit:
        path.append(currentStep)
        openPositions, openPositionsDict,closedPositions = getOpenandClosedPositions(currentStep)
        closedPositions.append(currentStep)
        
        if i != 0:          
            for pos in openPositions:
                if openPositionsDict[(pos.x, pos.y)] == currentDirection and pos not in closedPositions:
                    currentStep = pos
                    break
                
                currentStep = random.choice(openPositions)
            currentDirection = openPositionsDict[(currentStep.x, currentStep.y)]
            if i % 300 == 0:
                currentDirection = random.choice(list(openPositionsDict.values()))

        else:
            currentStep = random.choice(openPositions)
            currentDirection = openPositionsDict[(currentStep.x, currentStep.y)]
        i+=1
    
    # Remove intersection points
    path2 = path.copy()
    for i in range(len(path2)-1):
        point = path2[i]
        nextpoint = path2[i+1]
        step = LineString([point, nextpoint])
        if step.intersection(poly).geom_type == 'MultiLineString':
            # print(step.intersection(poly), point, nextpoint)
            if nextpoint in path:
                path.remove(nextpoint)
            path.remove(point)
            
    # Remove duplicates
    pathnew = []
    for point in path:
        pathnew.append((point.x,point.y))
    pathnew = list(dict.fromkeys(pathnew))
    for point in pathnew:
        plt.plot(point[0], point[1], 'bo', markersize = 2)
    return pathnew

trajcoords = obtainRandomTrajectory(xmax,ymax,routerPoint,poly)
plt.show()


def getTrajectoryKValueDictionary(trajcoords, kvaluesdict, kvalpolys):
    trajectoryKValueDictionary = {}

    
    for coord in trajcoords:
        for i in range(len(kvalpolys)):
            coordPoint = Point(coord)
            if coordPoint.within(kvalpolys[i]):
                if coord not in trajectoryKValueDictionary:
                    trajectoryKValueDictionary[coord] = i
    return trajectoryKValueDictionary



trajectoryKValueDictionary = getTrajectoryKValueDictionary(trajcoords, kvaluesdict, kvalpolys)
# trajectoryKValueDictionary2 = getTrajectoryKValueDictionary(trajcoords, kvaluesdict, kvalpolys)
