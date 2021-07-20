import matplotlib.pyplot as plt
import vertices2
from shapely.geometry import  Point, Polygon, LineString
import numpy as np
import math
from shapely.ops import polygonize
from descartes import PolygonPatch
from shapely.ops import cascaded_union

# Create list of points from given vertices
with open("mapEdges.txt") as f:
    content = f.readlines() 
f.close()
content = [x.strip() for x in content] 

# Define floor map and plot
contour = np.squeeze(vertices2.contours[0])
poly = Polygon(contour)
plt.plot(*poly.exterior.xy, 'k',linewidth=2.0)
verticesArray = vertices2.corners
print(*poly.exterior.coords,'\n')

# Define plot x limits and y limits
coordinates = list(poly.exterior.coords)
coords2 = np.array(coordinates)
xcoords, ycoords = coords2[:,0], coords2[:,1]
xmin, xmax = min(xcoords), max(xcoords)
ymin, ymax = min(ycoords), max(ycoords)
plt.xlim(xmin - 100, xmax + 100)
plt.ylim(ymin - 100, ymax+100)

# Obtain a router point at a randomly placed location
routerPoint = poly.representative_point()
routerx, routery = routerPoint.x, routerPoint.y-200
routerPoint = Point(routerx, routery)
routerpt = (routerx,routery)
for point in coordinates:
    px, py = point[0], point[1]
    # plt.plot(px, py, 'bo')    
plt.plot(routerx,routery, 'ko')
# Count intersections for rays drawn to each vertex
vertexIntersections={}
eps = 50
for point in coordinates:
    rc = LineString([routerPoint, point])
    plt.plot(*rc.xy, 'b', linewidth=0.75)
    if rc.intersects(poly):
        intersection = rc.intersection(poly)
        if intersection.geom_type == 'MultiLineString':
            numIntersections=len(intersection)
            for linestring in intersection:
                if linestring == intersection[0]:
                    comparept = np.array(linestring.coords[1]) 
                    pt = np.array(point)
                    distance = int(np.linalg.norm(pt-comparept))
                    if distance < eps:
                        numIntersections-=1
                if linestring == intersection[len(intersection)-1]:
                    numIntersections-=1
            vertexIntersections[point] = numIntersections
        elif intersection.geom_type == 'LineString':
            # LineStrings always occur from routerpt to the point 
            # so they can be discarded
            numIntersections=0
            vertexIntersections[point] = numIntersections
        elif intersection.geom_type == 'GeometryCollection':
            numIntersections=len(intersection)-1 # discard the point at beginning of geometrycollection
            compare = intersection[len(intersection)-1]
            comparept = np.array(compare.coords[1])
            pt = np.array(point)
            distance = int(np.linalg.norm(pt-comparept))
            if distance < eps:
                numIntersections-=1
            vertexIntersections[point] = numIntersections

# Identify kval segments on polygon for vertices
segmentLinesDict={}
for i in range(len(coordinates)):
   if i < len(coordinates)-1:
       p1 = coordinates[i]
       p2 = coordinates[i+1]
       segval1 = vertexIntersections[p1]
       segval2 = vertexIntersections[p2]
       line=(p1,p2)
       if segval1 == segval2 :
            if segval1 not in segmentLinesDict:
                 segmentLinesDict[segval1] = [line]
            else:
                 segmentLinesDict[segval1].append(line)  
ax=plt.gca() 
# # Connect segments between vertices for desired k value          
# def getKRegionVertexLines(kvalue, coordinates, segmentLinesDict,routerpt,facecolor):   
#     kvaluesegments=[]
#     for key in segmentLinesDict:
#         if key == kvalue:
#             kvaluesegments = kvaluesegments + segmentLinesDict[key]
#         if key < kvalue:
#             kvaluesegments = kvaluesegments+segmentLinesDict[key]
#     for i in range(len(coordinates)):
#         if i < len(coordinates)-1:
#              p1 = coordinates[i]
#              p2 = coordinates[i+1]
#              segval1 = vertexIntersections[p1]
#              segval2 = vertexIntersections[p2]
#              line=(p1,p2)
#              if segval1 == kvalue-1 and segval2 == kvalue: #TODO make iterative
#                  kvaluesegments.append(line)
#              elif segval1 == kvalue-2 and segval2 == kvalue-1:
#                  kvaluesegments.append(line)
#              elif segval1 == kvalue-3 and segval2 == kvalue-2:
#                  kvaluesegments.append(line)
#     totalpolygons = []
#     for segment in kvaluesegments:
#         p1,p2 = segment[0], segment[1]
#         line1 = (p1,p2)
#         line2 = (p1, routerpt)
#         line3 = (p2, routerpt)
#         region = list(polygonize((line1,line2, line3)))
#         poly = region[0]
#         totalpolygons.append(poly)
#         polygon_final = cascaded_union(poly)
#         # kfill = PolygonPatch(polygon_final,facecolor='#cccccc', edgecolor='None')
#         # ax.add_patch(kfill)
#     return totalpolygons


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

qIntersections={}

for coord in coordinates:
    extendedpoint = extendRay(routerPoint, coord)
    extendedray = LineString([routerPoint, extendedpoint])
    plt.plot(*extendedray.xy,'k', linewidth=0.25)
    if extendedray.intersects(poly):
        intersection = extendedray.intersection(poly)
        if intersection.geom_type == 'LineString':
            numIntersections=0
            qIntersections[coord] = numIntersections
        elif intersection.geom_type == 'GeometryCollection':
            numIntersections = len(intersection)

            for geometry in intersection:
                if geometry == intersection[0]:
                    numIntersections-=1 # discard Point in geometrycollection
                if geometry == intersection[1]:
                    comparept = np.array(geometry.coords[1])
                    pt = np.array(coord)
                    distance = int(np.linalg.norm(pt-comparept))
                    if distance < eps:
                        numIntersections-=1
            lastline = intersection[len(intersection)-1]
            intersectionpt = lastline.coords[1]
            qIntersections[intersectionpt] = numIntersections
        elif intersection.geom_type == 'MultiLineString':
            numIntersections = len(intersection)-1
            lastline = intersection[len(intersection)-1]
            intersectionpt = lastline.coords[1]
            # print(coord, '|', intersection, '|', numIntersections, '|=====', intersectionpt)
            doublewallpt1 = np.array(intersection[0].coords[1])
            doublewallpt2 = np.array(intersection[1].coords[0])
            distance = int(np.linalg.norm(doublewallpt1 - doublewallpt2))
            # print(doublewallpt1, doublewallpt2, distance)
           
            qIntersections[intersectionpt] = numIntersections

qpoints = list(qIntersections.keys())
qlinesdict={}
for i in range(len(qpoints)):
   if i > 0:
       p1 = qpoints[i]
       p2 = qpoints[i-1]
       segval1 = qIntersections[p1]
       segval2 = qIntersections[p2]
       line=(p1,p2)
       if segval1 == segval2:
           if segval1 not in qlinesdict:
                 qlinesdict[segval1] = [line]
           else:
                 qlinesdict[segval1].append(line)  

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
               coordinates.insert(i+1, tuple(p3))
               break
       i+=1

for q in qpoints:
    insertQ(coordinates, q)

# Remove any duplicates from new coordinates list
coordinates = list(dict.fromkeys(coordinates))
        
def getPointValue(point, vertexIntersections, qIntersections):
    segval = None
    if point in vertexIntersections.keys():
        segval = vertexIntersections[point]
        return segval
    elif point in qIntersections.keys():
        segval = qIntersections[point]
        return segval
    return segval

pointValuesDict={}
for coord in coordinates:
    pointval = getPointValue(coord, vertexIntersections, qIntersections)
    if coord not in pointValuesDict:
        pointValuesDict[coord] = pointval
finalSegmentLinesDict={}     
for i in range(len(coordinates)):
    if i < len(coordinates) - 1:
        pt1 = coordinates[i]
        pt2 = coordinates[i+1]
        segval1 = getPointValue(pt1, vertexIntersections, qIntersections)
        segval2 = getPointValue(pt2, vertexIntersections, qIntersections)
        line=(pt1,pt2)
        segmentvalue = segval1
        if segval1 == segval2:
            if segmentvalue not in finalSegmentLinesDict:
                finalSegmentLinesDict[segmentvalue] = [line]
            else:
                finalSegmentLinesDict[segmentvalue].append(line)
        if segval2 == segval1 + 1 or segval1 == segval2 + 1:
            if segmentvalue not in finalSegmentLinesDict:
                finalSegmentLinesDict[segmentvalue] = [line]
            else:
                finalSegmentLinesDict[segmentvalue].append(line)
    i+=1
            
        
# Connect segments between vertices for desired k value          
def getKRegionVertexLines(kvalue, coordinates, pointValuesDict, finalSegmentLinesDict,routerpt,facecolor):   
    kvaluesegments=[]
    for key in finalSegmentLinesDict:
        if key == kvalue:
            kvaluesegments = kvaluesegments + finalSegmentLinesDict[key]
        if key < kvalue:
            kvaluesegments = kvaluesegments + finalSegmentLinesDict[key]
    for i in range(len(coordinates)):
        if i < len(coordinates)-1:
              p1 = coordinates[i]
              p2 = coordinates[i+1]
              print(p1, p2)
              segval1 = pointValuesDict[p1]
              segval2 = pointValuesDict[p2]
              line=(p1,p2)
              # if kvalue == 0:
              # if (segval1 == kvalue and segval2 == kvalue+1) or ((segval2 == kvalue and segval1 == kvalue+1)):
              #    kvaluesegments.append(line)
              # if (segval1 == kvalue and segval2 == kvalue-1) or (segval2 == kvalue and segval1 == kvalue-1) : 
              #     kvaluesegments.append(line)
              # if (segval1 == kvalue-2 and segval2 == kvalue-3):
              #     kvaluesegments.append(line)
                 

    totalpolygons = []
    for segment in kvaluesegments:
        p1,p2 = segment[0], segment[1]
        line1 = (p1,p2)
        line2 = (p1, routerpt)
        line3 = (p2, routerpt)
        region = list(polygonize((line1,line2, line3)))
        poly = region[0]
        totalpolygons.append(poly)
        polygon_final = cascaded_union(poly)
        kfill = PolygonPatch(polygon_final,facecolor='#cccccc', edgecolor='None')
        ax.add_patch(kfill)
    return totalpolygons      

    


getKRegionVertexLines(0, coordinates, pointValuesDict, finalSegmentLinesDict,routerpt,'red')


# def getKRegionIntersectionLines(kvalue, qpoints, qlinesdict,routerpt, qIntersections, facecolor):
#     kvaluesegments=[]
#     for key in qlinesdict:
#         if key == kvalue:
#             kvaluesegments = kvaluesegments+qlinesdict[key]
#         if key < kvalue:
#             kvaluesegments = kvaluesegments+qlinesdict[key]
#     for i in range(len(qpoints)):
#         if i < len(qpoints)-1:
#              p1 = qpoints[i]
#              p2 = qpoints[i+1]
#              segval1 = qIntersections[p1]
#              segval2 = qIntersections[p2]
#              line=(p1,p2)
#              if segval1 == kvalue-1 and segval2 == kvalue: 
#                  kvaluesegments.append(line)
#              elif segval1 == kvalue-2 and segval2 == kvalue-1:
#                  kvaluesegments.append(line)
#              elif segval1 == kvalue-3 and segval2 == kvalue-2:
#                  kvaluesegments.append(line)
#              elif segval1 == kvalue-4 and segval2 == kvalue-3:
#                  kvaluesegments.append(line)
#              elif segval1 == kvalue-5 and segval2 == kvalue-4:
#                  kvaluesegments.append(line)
#     totalpolygons = []
#     for segment in kvaluesegments:
#         p1,p2 = segment[0], segment[1]
#         line1 = (p1,p2)
#         line2 = (p1, routerpt)
#         line3 = (p2, routerpt)
#         region = list(polygonize((line1,line2, line3)))
#         poly = region[0]
#         totalpolygons.append(poly)
#         polygon_final = cascaded_union(poly)
#         # kfill = PolygonPatch(polygon_final,facecolor='#cccccc', edgecolor='None')
#         # ax.add_patch(kfill)   
#     return totalpolygons
        
# def getKRegion(kvalue,qpoints, qlinesdict, qIntersections,coordinates, segmentLinesDict,routerpt, facecolor):
#     regionpolys1=getKRegionVertexLines(kvalue, coordinates, segmentLinesDict,routerpt,facecolor)    
#     regionpolys2=getKRegionIntersectionLines(kvalue, qpoints, qlinesdict,routerpt, qIntersections, facecolor)    
#     kregion = regionpolys1 + regionpolys2
#     polygon_final1 = cascaded_union(regionpolys1)
#     polygon_final2 = cascaded_union(regionpolys2)
#     kfill1 = PolygonPatch(polygon_final1,facecolor='#cccccc', edgecolor='None')
#     kfill2 = PolygonPatch(polygon_final2,facecolor='#cccccc', edgecolor='None')
#     ax.add_patch(kfill1)
#     ax.add_patch(kfill2)
    
    
# kvals = list(qlinesdict.keys())
# kvals.sort()
# facecolors=['red','yellow','blue','green','orange', 'magenta', 'navy']
# # for i in range(len(kvals)+1):
# #     print(i, facecolors[i])
# #     getKRegion(i, qpoints, qlinesdict, qIntersections, coordinates, segmentLinesDict, routerpt,facecolors[i])

# getKRegion(0, qpoints, qlinesdict, qIntersections, coordinates, segmentLinesDict, routerpt,'red')
plt.show()


