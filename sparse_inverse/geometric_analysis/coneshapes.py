''' Given a trajectory and its associated k-values, draw refined cone shapes which are completely k-visible.'''
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon, MultiPoint
from shapely.ops import polygonize
from shapely.ops import cascaded_union

def getRefinedConeShapes(trajectory_kvalues, grid_width, grid_height):
    trajectoryKValueDictionary = trajectory_kvalues[0]
    trajectoryCoordinates = list(trajectoryKValueDictionary.keys())
    routerCoords = trajectory_kvalues[1]
    
    # Create a dictionary of every coordinate and its k value
    def getKValueDictionary(trajectoryKValueDictionary):  
        k_val_dictionary = {}
        for i in range(grid_height):
            for j in range(grid_width):
                coordinate = (j,i)
                k_val_dictionary[coordinate] = None
        for coord in trajectoryKValueDictionary:
            k_val_dictionary[coord] = trajectoryKValueDictionary[coord]
        return  k_val_dictionary
    
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