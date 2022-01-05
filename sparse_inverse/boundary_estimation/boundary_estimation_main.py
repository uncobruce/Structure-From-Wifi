''' Given a dictionary of kvalues: coneshapes, estimate wall locations and return their coordinates.'''

from shapely.geometry import Point, Polygon, MultiPoint, LineString, MultiLineString
from shapely.ops import polygonize, cascaded_union
from shapely import affinity
from bresenham import bresenham
import numpy as np
import math
import boundary_estimation.vertical_boundary_estimation as vertical_boundary_estimation 
import boundary_estimation.horizontal_boundary_estimation as horizontal_boundary_estimation 
import grid_mapping.grid_map as grid_map


def boundaryEstimation(kvalue_coneshapes, trajectory_kvalues):
    # Initialize new gridmap for estimated wall coordinates
    estimatedMap = grid_map.GridMap('')
    estimatedMap.plotTrajectory(trajectory_kvalues)
    
    total_wall_coordinates = []
    
    # Identifying Outer Walls
    outer_wall_coords = outerWallCoordinates(trajectory_kvalues)
    total_wall_coordinates += outer_wall_coords
    
    # Identifying Inner Walls
    for kval in kvalue_coneshapes:
        if kval == 0: continue
        poly = kvalue_coneshapes[kval]
        prevpoly = previousPolygon(kvalue_coneshapes[kval-1], poly) 
        inner_line_segments=[]
        if type(poly) == list: # if multiple polys for kvalue
            for p in poly:
                wall_coordinates = polygonHandler(p, prevpoly)
                if poly.index(p) == 0:
                    constant_value, constant_index = getWallConstants(wall_coordinates)
                else:
                    wall_coordinates = smoothCoordinates(wall_coordinates, constant_value, constant_index)
                total_wall_coordinates+=wall_coordinates
                inner_line_segments.append(wall_coordinates)
        if type(poly) == Polygon: # only one polygon 
            wall_coordinates = polygonHandler(poly, prevpoly)
            total_wall_coordinates += wall_coordinates
            inner_line_segments.append(wall_coordinates)
        extended_segments = mapCompletion(inner_line_segments, outer_wall_coords)
        for seg in extended_segments:
            total_wall_coordinates += seg
  
    # Remove coordinates coinciding with the trajectory
    trajectory = list(trajectory_kvalues[0].keys())
    for coord in trajectory:
        if coord in total_wall_coordinates:
            total_wall_coordinates.remove(coord)
    
    estimatedMap = estimatedMap.plotWallCoordinates(total_wall_coordinates)    
    
    return total_wall_coordinates


def getWallConstants(wall_coordinates):
    if wall_coordinates == []: return None, None
    startpt, endpt = wall_coordinates[0], wall_coordinates[-1]
    if startpt[0] == endpt[0]:
        return startpt[0], 0
    elif startpt[1] == endpt[1]:
        return startpt[1], 1

def smoothCoordinates(wall_coordinates, constant_value, constant_index): 
    ''' Ensure coordinates have the same constant (x/y) value'''
    new_wall_coordinates=[]
    for coord in wall_coordinates:
        if constant_index == 0:
            new_coord = (constant_value, coord[1])
            new_wall_coordinates.append(new_coord)
        elif constant_index == 1:
            new_coord = (coord[0], constant_value)
            new_wall_coordinates.append(new_coord)
    
    return new_wall_coordinates


def closestpoint(outer_wall_coords, point):
    shortest_dist = None
    closest_point = None
    for coord in outer_wall_coords:
        norm = np.linalg.norm(np.array(point)-np.array(coord))
        if shortest_dist == None or norm < shortest_dist:
            closest_point = coord
            shortest_dist = norm
    return closest_point, shortest_dist

def extendLine(segment, extension_point, end_point, index_of_interest):
    if index_of_interest == 0: # extending horizontally
        j = extension_point[1]
        extended_segment=[]
        start, end = min(extension_point[0], end_point[0]), max(extension_point[0], end_point[0])
        for i in range(start, end):
            extended_segment.append((i,j))
    elif index_of_interest == 1: # extending vertically
        i = extension_point[0]
        extended_segment = []
        start, end = min(extension_point[1], end_point[1]), max(extension_point[1], end_point[1])
        for j in range(start, end):
            extended_segment.append((i,j))

    return extended_segment

def decomposeSegment(segment):
    # return segments in order of [horizontal segment, vertical segment]
    horizontal_segment, vertical_segment = None, None
    start1, start2 = segment[0], segment[1]
    if start1[0] == start2[0]: 
        horizontal_segment = [start1]
        for coord in segment:
            if coord == start1: continue
            if coord[0] == start1[0]:
                horizontal_segment.append(coord)
            else:
                vertical_segment = [coord]
                break
        for coord in segment:
            if coord == vertical_segment[0]: continue
            if coord[1] == vertical_segment[0][1]:
                vertical_segment.append(coord)
    
    elif start1[1] == start2[1]:
        vertical_segment = [start1]
        for coord in segment: 
            if coord == start1: continue
            if coord[1] == start1[1]:
                vertical_segment.append(coord)
            else:
                horizontal_segment = [coord]
                break
        for coord in segment:
            if coord == horizontal_segment[0]: continue
            if coord[0] == horizontal_segment[0][0]:
                horizontal_segment.append(coord)
                
    
    return[horizontal_segment, vertical_segment]
            
    

def mapCompletion(inner_line_segments, outer_wall_coords):
    # For every inner line segment, choose one endpoint to extend until it encounters another wall
    extended_segs=[]
    decomposed_segs=[] # segments with both horiz and vertical component
    for seg in inner_line_segments:
        if seg == []: continue
        startpt, endpt = seg[0], seg[-1]
        if startpt[0] == endpt[0]: index_of_interest = 1 # xval constant; extend along y
        elif startpt[1] == endpt[1]: index_of_interest = 0 #yval constant; extend along x
        else:
            decomposed_segments = decomposeSegment(seg)
            decomposed_segs += decomposed_segments
            continue
            
        closest_point_to_start, start_dist = closestpoint(outer_wall_coords, startpt)
        closest_point_to_end, end_dist = closestpoint(outer_wall_coords, endpt)
        
        if start_dist < end_dist:
            extended_segment = extendLine(seg, startpt, closest_point_to_start, index_of_interest)
            extended_segs.append(extended_segment)
        elif end_dist < start_dist:
            extended_segment = extendLine(seg, endpt, closest_point_to_end, index_of_interest)
            extended_segs.append(extended_segment)
        
    for seg in decomposed_segs:
        if seg == []: continue
        startpt, endpt = seg[0], seg[-1]
        if startpt[0] == endpt[0]: index_of_interest = 1 # xval constant; extend along y
        elif startpt[1] == endpt[1]: index_of_interest = 0 #yval constant; extend along x
        closest_point_to_start, start_dist = closestpoint(outer_wall_coords, startpt)
        closest_point_to_end, end_dist = closestpoint(outer_wall_coords, endpt)
        
        if start_dist <= end_dist:
            extended_segment = extendLine(seg, startpt, closest_point_to_start, index_of_interest)
            extended_segs.append(extended_segment)
        elif end_dist < start_dist:
            extended_segment = extendLine(seg, endpt, closest_point_to_end, index_of_interest)
            extended_segs.append(extended_segment)
      
            
        
    return extended_segs


def outerWallCoordinates(trajectory_kvalues, offset_distance=1.1):
    '''
        Return a list of grid coordinates corresponding to the smallest envelope encompassing the coordinates
        of the trajectory and the inner walls identified
        :type trajectory_kvalues: list with 2 elements: [dict of {coord: kval}, (routerx, routery)]
        :rtype: list
    '''
    outer_wall_coords = []
    trajectory = list(trajectory_kvalues[0].keys())
    trajectoryMultiPoint = MultiPoint(trajectory)
    outer_wall_corners = trajectoryMultiPoint.envelope
    outer_wall_corners = list(outer_wall_corners.exterior.coords)
    outer_wall_lines = []
    for i in range(len(outer_wall_corners)-1):
        point1 = outer_wall_corners[i]
        point2 = outer_wall_corners[i+1]
        linestring = LineString([point1, point2])
        outer_wall_lines+=list(linestring.coords)
    
    inner_bounding_box = Polygon(outer_wall_lines)
    inner_bounding_box_scaled = affinity.scale(inner_bounding_box, xfact=offset_distance, yfact=offset_distance)
    
    outer_wall_lines=list(inner_bounding_box_scaled.exterior.coords)
    for i in range(len(outer_wall_lines)-1):
        p1 = (int(outer_wall_lines[i][0]), int(outer_wall_lines[i][1]))
        p2 = (int(outer_wall_lines[i+1][0]), int(outer_wall_lines[i+1][1]))
        
        line = list(bresenham(p1[0],p1[1], p2[0],p2[1]))
        outer_wall_coords+=line
    return outer_wall_coords




def previousPolygon(prevpoly, poly):
    '''
    Given a list of polygons OR a Polygon with kvalue = ki, return the one which is touching the kj polygon to be used for comparsion
    :rtype: Polygon
    '''
    if type(prevpoly) == Polygon:
        return prevpoly
    elif type(prevpoly) == list:
        for p in prevpoly:
            if p.intersects(poly):
                return p




def slope(x1, y1, x2, y2):
    if abs(x2-x1) == 0:
        return math.inf
    slope = (y2-y1)/(x2-x1)
    return slope

def wallType(intersection):
    ''' Determine whether wall is vertical or horizontal based on intersection slope'''
    eps1, eps2, alpha = 8, .7, 1
    x1, y1, x2, y2 = intersection.coords[0][0], intersection.coords[0][1], intersection.coords[1][0], intersection.coords[1][1]
    m = slope(x1, y1, x2, y2)
    norm = np.linalg.norm(np.array([x2,y2])-np.array([x1,y1])) # exclude lines with endpoints too close to one another
    
    if (abs(m) > eps1) and norm > alpha:
        return("vertical")
    elif (abs(m) < eps2) and norm > alpha:
        return("horizontal")


def polygonHandler(poly, prevpoly):
    ''' :type poly: current kj Polygon (k_i-1) polygon being analyzed for walls
        :type prevpoly: ki Polygon being compared with kj polygon
        :rtype: wall coordinates 
    '''
    # Wall is located in the same direction as the intersection line
    intersection = poly.intersection(prevpoly)
    wall_coordinates = []  
    if intersection.geom_type == 'GeometryCollection':
        for inter in intersection:
            if inter.geom_type == 'LineString':
                wall_type = wallType(inter)
                if wall_type == 'vertical': 
                    # print("Vertical wall found")
                    wall_coordinates += vertical_boundary_estimation.polygonVerticalWallCoordinates(poly, inter)   
                elif wall_type == 'horizontal':
                    wall_coordinates += horizontal_boundary_estimation.polygonHorizontalWallCoordinates(poly, inter)   
           
    elif intersection.geom_type == 'LineString':
        wall_coordinates = []
        wall_type = wallType(intersection)
        if wall_type == 'vertical': 
            # print("Vertical wall found") 
            wall_coordinates += vertical_boundary_estimation.polygonVerticalWallCoordinates(poly, intersection)
        elif wall_type == 'horizontal':
            wall_coordinates += horizontal_boundary_estimation.polygonHorizontalWallCoordinates(poly, inter)   
    elif intersection.geom_type == 'MultiLineString':
       wall_coordinates = []
       for inter in intersection:
            if inter.geom_type == 'LineString':
                wall_type = wallType(inter)
                if wall_type == 'vertical': 
                    wall_coordinates += vertical_boundary_estimation.polygonVerticalWallCoordinates(poly, inter)   
                elif wall_type == 'horizontal':
                    wall_coordinates += horizontal_boundary_estimation.polygonHorizontalWallCoordinates(poly, inter)   
    return wall_coordinates

