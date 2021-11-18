import matplotlib.pyplot as plt
from shapely.geometry import  Point, Polygon, LineString
import numpy as np
import math
from shapely.ops import polygonize
from descartes import PolygonPatch
from shapely.ops import cascaded_union
from matplotlib import colors as colors
''' Given contour coordinates, plot k-visibility region.'''
def plotKVisRegion(contour_coordinates, showPlot=True, showBorders=False, saveImage=True):
    # Define floor map based on vertices2.py and plot
    contour = np.squeeze(contour_coordinates)
    poly = Polygon(contour)
    
    def removeClosePoints(points):
        points2 = points.copy()
        for i in range(len(points2)-1):
            p1 = np.array(points2[i])
            p2 = np.array(points2[i+1])
            distance = np.linalg.norm(p2-p1)
            if distance < 6:
                points.remove(points2[i])
        return points
    
    # Define plot x limits and y limits
    coordinates = list(poly.exterior.coords)
    coords2 = np.array(coordinates)
    xcoords, ycoords = coords2[:,0], coords2[:,1]
    xmin, xmax = min(xcoords), max(xcoords)
    ymin, ymax = min(ycoords), max(ycoords)
    
    
    
    # Define bounding box poly
    bbox = Polygon([(xmin-100, ymin-100), (xmax+100, ymin-100), (xmax+100, ymax+100), (xmin-100, ymax+100)])
    
    # Obtain a router point at a randomly placed location
    routerPoint = poly.representative_point()
    routerx, routery = routerPoint.x, routerPoint.y-200
    routerPoint = Point(routerx, routery)
    routerpt = (routerx,routery)
    for point in coordinates:
        px, py = point[0], point[1]
    
    def getZPoint(routerPoint):
        extendedpt = (routerPoint.x+10000, routerPoint.y)
        horizray = LineString([routerPoint, extendedpt])
        intersection = horizray.intersection(poly)
        # print(intersection)
        if intersection.geom_type == 'LineString':
            intersectionpt = (intersection.coords[1][0], intersection.coords[1][1])
        elif intersection.geom_type == 'MultiLineString':
            intersectionpt = (intersection[0].coords[1][0], intersection[0].coords[1][1])
            # print(intersectionpt)
        return intersectionpt
    
    # Obtain point z at a point on the wall directly horizontal to the router point - to be used in Step 3
    z = getZPoint(routerPoint)
    maxzdistance = 200
    pt1 = np.array(z)
    pt2 = np.array(routerpt)
    distancetoz = np.linalg.norm(pt2-pt1)
    
    # For cases where the router is in a hallway position or is too close to the wall, removing close points
    # results in a strange map. Otherwise it is necessary to remove points too close to each other due to
    # the double wall effect.
    if distancetoz > maxzdistance or (abs(routerx - xmax) < 100 or abs(routery-ymax)<100):
        coordinates = removeClosePoints(coordinates)
        
    # Plot coordinates of contour shape
    for point in coordinates:
        px, py = point[0], point[1]
    

    
    # Reverse coordinates so that they appear in CCW order around the polygon
    coordinates.reverse()
    
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
    
    # Look through all coordinates and determine which of them are critical vertices
    criticalvertices=[]
    for i in range(1,len(coordinates)-1):
        vi = coordinates[i]
        viprev = coordinates[i-1]
        vinext = coordinates[i+1]
        criticalRay = LineString([routerPoint, vi])
        if isVertexCritical(criticalRay, viprev, vinext):
            criticalvertices.append(vi)
    
    # STEP 2) Checking ray-poly intersections
    # -------------------------------------------------------------------------
    def extendRay(routerPoint, vertex):
        x1, y1 = routerPoint.x, routerPoint.y
        x2, y2 = vertex[0], vertex[1]
        extendLength = 10000
        diff = (x2-x1, y2-y1)
        mag = math.sqrt((x2-x1)**2 + (y2-y1)**2)
        norm = (diff[0] / mag, diff[1]/mag) 
        p3 = (vertex[0] + extendLength*norm[0],vertex[1] + extendLength*norm[1])
        x3,y3 = p3[0], p3[1]
        return (x3,y3)
    
    intpoints = {}
    qpoints = []
    def closePoints(p1,p2):
        # return True if points are close
        point1 = np.array(p1)
        point2 = np.array(p2)
        distance = int(np.linalg.norm(point2-point1))
        if distance < 5:
            return True
        return False
    
    # Extend a ray from all critical vertices and observe the location of intersection points with the polygon
    for critv in criticalvertices:
        extendedpt = extendRay(routerPoint, critv)
        intersectionRay = LineString([critv, extendedpt])
        intpoints[critv] = []
        # plt.plot(*intersectionRay.xy, 'k--')
        intersection = intersectionRay.intersection(poly)
        if intersection.geom_type == 'LineString':
            intersectionpt = intersection.coords[1]
            intersectionpt = (int(intersectionpt[0]), int(intersectionpt[1]))
            intpoints[critv].append(intersectionpt)
            qpoints.append(intersectionpt)
            # plt.plot(intersectionpt[0],intersectionpt[1], 'ko')
            
        elif intersection.geom_type == 'GeometryCollection':
            for geometry in intersection:
                if geometry.geom_type == 'Point': pass
                elif geometry.geom_type == 'LineString':
                    intersectionpt1 = (int(geometry.coords[0][0]), int(geometry.coords[0][1]))
                    intersectionpt2 = (int(geometry.coords[1][0]), int(geometry.coords[1][1]))
                    if not closePoints(intersectionpt1, critv):
                        intpoints[critv].append(intersectionpt1)
                        intpoints[critv].append(intersectionpt2)
                        # plt.plot(intersectionpt1[0],intersectionpt1[1],'ko')
                        qpoints.append(intersectionpt1)
                        qpoints.append(intersectionpt2)
                    else:
                        intpoints[critv].append(intersectionpt2)
                        qpoints.append(intersectionpt2)
                    # plt.plot(intersectionpt2[0],intersectionpt2[1],'ko')
             
        elif intersection.geom_type == 'MultiLineString':
            intersectionpts = []
            for line in intersection:
                if line == intersection[0]:
                    intersectionpt = (int(line.coords[1][0]), int(line.coords[1][1]))
                    if not closePoints(intersectionpt, critv):
                        qpoints.append(intersectionpt)
                        intpoints[critv].append(intersectionpt)
                        # plt.plot(intersectionpt[0],intersectionpt[1], 'ko')
                else:
                    pt1 = (int(line.coords[0][0]), int(line.coords[0][1]))
                    pt2 = (int(line.coords[1][0]), int(line.coords[1][1]))
                    intpoints[critv].append(pt1)
                    intpoints[critv].append(pt2)
                    qpoints.append(pt1)
                    qpoints.append(pt2)
                    # plt.plot(pt1[0], pt1[1], 'ko')
                    # plt.plot(pt2[0], pt2[1], 'ko')
        
        
    # Applying +1/-1 rule
    def isLeftTurn(vi, viPrev, viNext):
        # given a vertex, determine if CW or CCW
        # returns True if CCW (left turn), returns False if CW (right turn)
        return ((vi[0] - viPrev[0])*(viNext[1]-vi[1]) - (vi[1]-viPrev[1])*(viNext[0]-vi[0]) > 0 )
    
    def onPositiveSide(vi, viPrev, routerx, routery):
        # given a vertex, determine if vPrev is on positive side of the ray 
        # ray is defined as line connecting transmitter coords to vi coords
        line = {'x1': routerx,'y1':routery,'x2':vi[0],'y2':vi[1]}
        p1 = {'x':viPrev[0],'y':viPrev[1]}
        return (( (line['y1'] - line['y2'])*(p1['x'] - line['x1'])+(line['x2']- line['x1'])*(p1['y']-line['y1']) )>0)
    
    
    pointIDs={} 
    for i in range(1,len(coordinates)-1):
        vi = coordinates[i]
        viprev = coordinates[i-1]
        vinext = coordinates[i+1]
        if vi in criticalvertices:
            if isLeftTurn(vi, viprev, vinext):
                  if onPositiveSide(vi, viprev, routerx, routery):
                      pointIDs[vi] = 1
                  else:
                      pointIDs[vi] = -1
            else:
                if onPositiveSide(vi, viprev, routerx, routery):
                    pointIDs[vi] = -1
                else:
                    pointIDs[vi] = 1
    # Applying +2/-2 rule
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
    # Create totalcoordinates, a list of all coordinates including intersection points
    totalcoordinates = coordinates.copy()
    for q in qpoints:
        insertQ(totalcoordinates, q)
    
    def get_v_j_prev(coordinates, q, qpoints):
        # Obtain closest coordinate on polygon to q point
        for i in range(len(coordinates)-1):
            pt1 = np.array(coordinates[i])
            pt2 = np.array(coordinates[i+1])
            pt3 = np.array(q)
            d12 = int(np.linalg.norm(pt2-pt1))
            d13 = int(np.linalg.norm(pt3-pt1))
            d23 = int(np.linalg.norm(pt2-pt3))
            if d12-1 == d13 + d23 or d12 == d13 + d23: # If a point is between two points on the polygon, then
                return tuple(pt1)                       # it is collinear with them and one of them is v_j_prev
    
        
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
    
    
    for i in range(1, len(coordinates)-1):
        vi = coordinates[i]
        viprev = coordinates[i-1]
        if vi in criticalvertices:
            qpts = intpoints[vi]
            if qpts != []:
                for q in qpts:
                    # print(q, vi, viprev)
                    vjprev = get_v_j_prev(coordinates, q,qpoints)
                    extendedpt = extendRay(routerPoint, vi)
                    rc = LineString([routerPoint, extendedpt])
                    if onSameSide(rc, vjprev, viprev):
                        pointIDs[q] = -2
                    else:
                        pointIDs[q] = 2
    
    # STEP 3) Constructing k-visibility regions
    # -------------------------------------------------------------------------
    # Insert point Z into totalcoordinates list
    insertQ(totalcoordinates, z)
    
    # Reorder totalcoordinates so that it starts from point z and proceeds around poly in CCW order
    totalcoordinates = totalcoordinates[totalcoordinates.index(z):] + totalcoordinates[0:totalcoordinates.index(z)]
    temp = totalcoordinates[1:]
    totalcoordinates = [totalcoordinates[0]] + temp
    
    # Create list of only critical vertices and q points
    critVerticesandQPoints = []
    for coord in totalcoordinates:
        if coord in criticalvertices:
            critVerticesandQPoints.append(coord)
        elif coord in qpoints:
            critVerticesandQPoints.append(coord)
        elif coord == totalcoordinates[0]:
            critVerticesandQPoints.append(coord)
    
    # Reorder critVerticesandQPoints so it also starts from point z and goes through list in order
    critVerticesandQPoints = critVerticesandQPoints[critVerticesandQPoints.index(z):] + critVerticesandQPoints[0:critVerticesandQPoints.index(z)]
    temp = critVerticesandQPoints[1:]
    critVerticesandQPoints = [critVerticesandQPoints[0]] + temp
    
    # Obtain edge segment vals, first to obtain max segmentval value to be used below
    polyvalue=0
    segmentvals2 = []
    for pt in critVerticesandQPoints:
        if pt == critVerticesandQPoints[0]:
            polyvalue=0
            segmentvals2.append(polyvalue) #keep track of segment "ahead" of pt
        else:
            ptID = pointIDs[pt]
            polyvalue = polyvalue + ptID
            if polyvalue < 0:
                polyvalue=0
            segmentvals2.append(polyvalue)
    
    segmentvals = []
    for pt in critVerticesandQPoints:
        if pt == critVerticesandQPoints[0]:
            polyvalue=0
            segmentvals.append(polyvalue) #keep track of segment "ahead" of pt
        else:
            ptID = pointIDs[pt]
            polyvalue = polyvalue + ptID
            if polyvalue < 0:
                polyvalue=0
            if distancetoz < maxzdistance and not (abs(routerx - xmax) < 100 or abs(routery-ymax)<100):
                if polyvalue > max(segmentvals2)-1: # Again a feature that is sometimes necessary when router is 
                    if abs(maxzdistance-distancetoz) < 100: # too close to the wall which causes program to 
                        polyvalue=polyvalue-1               # behave strangely. For this reason we obtained
                    else:                                   # max(segmentvals2) above which fixes the issue
                        polyvalue=polyvalue-2
            segmentvals.append(polyvalue)
            
    # Represent all coords by their next segment vals
    segmentvalsdict = {}
    for i in range(len(critVerticesandQPoints)):
        point = critVerticesandQPoints[i]
        segmentvalsdict[point] = segmentvals[i]
    currentsegval = None
    for coord in totalcoordinates:
        if coord in critVerticesandQPoints:
            currentsegval = segmentvalsdict[coord]
        else:
            segmentvalsdict[coord] = currentsegval
    
    # Create list and dictionary of all edge segments along with their segment values
    segmentLines=[]
    segmentLinesDict={}
    for i in range(len(totalcoordinates)):       
        if i == len(totalcoordinates)-1:
            pt1=totalcoordinates[i]
            pt2=totalcoordinates[0]
        else:
            pt1 = totalcoordinates[i]
            pt2 = totalcoordinates[i+1]    
        line = (pt1,pt2)
        segmentLines.append(line)
        segmentvalue = segmentvalsdict[pt1]
        segmentvalue2 = segmentvalsdict[pt2]
    
        if segmentvalue not in segmentLinesDict:
            segmentLinesDict[segmentvalue] = [line]
        else:
            segmentLinesDict[segmentvalue].append(line)
    
    
    # Functions to plot k visibility polygons within the map
    def getKRegionPolygonLines(kvalue, coordinates, segmentLinesDict,routerpt):   
        kvaluesegments=[]
        for key in segmentLinesDict:
            if key <= kvalue:
                kvaluesegments = kvaluesegments + segmentLinesDict[key]
        totalpolygons = []
        for segment in kvaluesegments:
            p1,p2 = segment[0], segment[1]
            line1 = (p1,p2)
            line2 = (p1, routerpt)
            line3 = (p2, routerpt)
            region = list(polygonize((line1,line2, line3)))
            if region != []:
                poly = region[0]
                totalpolygons.append(poly)
        return totalpolygons    
    
    def getKRegion(kvalueinput,kvalue, coordinates, segmentLinesDict,routerpt):
        if kvalueinput == 0:
            kvalue = 0
        else:
            kvalue = kvalueinput *2+1
        kregion = getKRegionPolygonLines(kvalue, coordinates, segmentLinesDict,routerpt)
        kregionpolys = [poly for poly in kregion]
        polygon_final = cascaded_union(kregionpolys)
        return polygon_final
    
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
    # =============================================================================
    # Dealing with bounding box points
    # =============================================================================
    # Record end-of-polygon points
    endofpolypts = []
    for point in totalcoordinates:
        pointx, pointy = point[0], point[1]
        if pointx == xmin or pointx == xmax or pointy == ymin or pointy == ymax:
            endofpolypts.append(point)
        elif abs(pointx-xmin)<2 or  abs(pointx-xmax)<2 or  abs(pointy-ymin)<2 or  abs(pointy-ymax)<2:
            endofpolypts.append(point)
    
    # # Record extreme points in bounding box
    bboxcoords = [(xmin-100, ymin-100), (xmax+100, ymin-100), (xmax+100, ymax+100), (xmin-100, ymax+100)]
    
    bbox_intpoints=[]
    bbox_segmentvalsdict = {}
    for point in endofpolypts:
        extendedpt = extendRay(routerPoint, point)
        extendedray = LineString([routerpt, extendedpt])
        # plt.plot(*extendedray.xy,'k--')
        intersection = extendedray.intersection(bbox)
        intersectionpt = (intersection.coords[1][0], intersection.coords[1][1])   
        kval=segmentvalsdict[point]+1
        # plt.plot(intersectionpt[0], intersectionpt[1],'ko')
        bbox_intpoints.append(intersectionpt)
        bbox_segmentvalsdict[intersectionpt] = kval
    
    bboxpts = list(bbox_segmentvalsdict.keys())
    
    
    bbox_segmentLinesDict={}
    for i in range(len(bboxpts)):
        if i != len(bboxpts)-1:
            pt1 = bboxpts[i]
            pt2 = bboxpts[i+1]
        else:
            pt1 = bboxpts[i]
            pt2 = bboxpts[0]
        segmentvalue = bbox_segmentvalsdict[pt1]
        line=(pt1,pt2)
        if segmentvalue not in bbox_segmentLinesDict.keys():
            bbox_segmentLinesDict[segmentvalue] = [line]
        else:
            bbox_segmentLinesDict[segmentvalue].append(line)
                
    # Functions to plot k visibility polygons within the map
    def getKRegionBBoxLines(kvalue, bboxpts, bbox_segmentLinesDict,routerpt):   
        kvaluesegments=[]
        for key in bbox_segmentLinesDict:
            if key <= kvalue:
                kvaluesegments = kvaluesegments + bbox_segmentLinesDict[key]
        totalpolygons = []
        for segment in kvaluesegments:
            p1,p2 = segment[0], segment[1]
            if p1[0] == p2[0] or p1[1] == p2[1]:
                line1 = (p1,p2)
                line2 = (p1, routerpt)
                line3 = (p2, routerpt)
                region = list(polygonize((line1,line2, line3)))
            else:
                if p1[0] < p2[0] and p2[1] < p1[1]:
                    line1 = (p1, (p1[0],p2[1]))
                    line2 = (line1[1], p2)
                    line3 = (p1, routerpt)
                    line4 = (p2, routerpt)
                    region = list(polygonize((line1,line2, line3,line4)))
                elif p1[0] < p2[0] and p2[1] > p1[1]:
                    line1 = (p1, (p2[0],p1[1]))
                    line2 = (line1[1], p2)
                    line3 = (p1, routerpt)
                    line4 = (p2, routerpt)
                    region = list(polygonize((line1,line2, line3,line4)))
                elif p1[0] > p2[0] and p2[1] < p1[1]:
                    line1 = (p1, (p2[0],p1[1]))
                    line2 = (line1[1], p2)
                    line3 = (p1, routerpt)
                    line4 = (p2, routerpt)
                    region = list(polygonize((line1,line2, line3,line4)))
                elif p1[0] > p2[0] and p2[1] > p1[1]:
                    line1 = (p1, (p1[0],p2[1]))
                    line2 = (line1[1], p2)
                    line3 = (p1, routerpt)
                    line4 = (p2, routerpt)
                    region = list(polygonize((line1,line2, line3,line4)))
                
            if region != []:
                poly = region[0]
                totalpolygons.append(poly)
        return totalpolygons    
    
    def getBBoxKRegion(kvalueinput, bboxpts, bbox_segmentLinesDict,routerpt):
        kvalue = kvalueinput *2
        kregion = getKRegionBBoxLines(kvalue, bboxpts, bbox_segmentLinesDict,routerpt)
        kregionpolys = [poly for poly in kregion]
        polygon_final = cascaded_union(kregionpolys)
        return polygon_final
    
    facecolors=['red','yellow','blue','green','orange', 'magenta', 'navy', 'teal', 'tan', 'lightsalmon','lightyellow','coral','rosybrown']
    kvaluescolordict={} # obtain kvalue: rgb val pairs
    for j in range(len(segmentLinesDict)-1,-1,-1):
        kvalue=j      
        for i in range(kvalue, -1,-1):
            if facecolors[j] not in kvaluescolordict:
                associated_rgba_value = colors.to_rgb(facecolors[j])
                color = (associated_rgba_value[0]*255, associated_rgba_value[1]*255, associated_rgba_value[2]*255)
                kvaluescolordict[color] = j
                
    if showPlot == True: # must set showPlot to True at least once for image to save in directory
        plt.xlim(xmin - 90, xmax + 90)
        plt.ylim(ymin - 90, ymax+90)
        ax=plt.gca()
        
        for j in range(len(bbox_segmentLinesDict),0,-1):
            kvalue=j 
            kregion_bbox=getBBoxKRegion(j, bboxpts, bbox_segmentLinesDict,routerpt)
            kfill_bbox = PolygonPatch(kregion_bbox,facecolor=facecolors[j], edgecolor='None')
            ax.add_patch(kfill_bbox)
        
       
        for j in range(len(segmentLinesDict)-1,-1,-1):
            kvalue=j
           
            for i in range(kvalue, -1,-1):
                kregion=getKRegion(j,kvalue, coordinates, segmentLinesDict,routerpt)
                kfill = PolygonPatch(kregion,facecolor=facecolors[j], edgecolor='None')
                if facecolors[j] not in kvaluescolordict:
                    associated_rgba_value = colors.to_rgb(facecolors[j])
                    color = (associated_rgba_value[0]*255, associated_rgba_value[1]*255, associated_rgba_value[2]*255)
                    kvaluescolordict[color] = j
                ax.add_patch(kfill)
        
            
        if saveImage == True: # Save image without borders
            plt.gca().set_axis_off()
            plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, 
                        hspace = 0, wspace = 0)
            plt.margins(0,0)
            plt.savefig('data_processing/kvis_plot.png')
        
        if showBorders == True: # Plot showing walls and router pt location
            plt.plot(*poly.exterior.xy,'k')
            plt.plot(routerx,routery, 'ko')    
    
        
     
            
   
    return (routerx,routery), (xmax, ymax), kvaluescolordict
        