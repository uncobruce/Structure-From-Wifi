''' Given a dictionary of kvalues: coneshapes, estimate wall locations and return their coordinates.'''

from shapely.geometry import Point, Polygon, MultiPoint, LineString, MultiLineString
from shapely.ops import polygonize, cascaded_union
from shapely import affinity
from bresenham import bresenham
import numpy as np
import math
import boundary_estimation.vertical_boundary_estimation as vertical_boundary_estimation 
import boundary_estimation.horizontal_boundary_estimation as horizontal_boundary_estimation 

def boundaryEstimation(kvalue_coneshapes, trajectory_kvalues):
    # Identifying Inner Walls
    total_wall_coordinates = []
    for kval in kvalue_coneshapes:
        if kval == 0: continue
        poly = kvalue_coneshapes[kval]
        prevpoly = previousPolygon(kvalue_coneshapes[kval-1], poly) 
        if type(poly) == list: # if multiple polys for kvalue
            for p in poly:
                wall_coordinates = polygonHandler(p, prevpoly)
                total_wall_coordinates+=wall_coordinates
        if type(poly) == Polygon: # only one polygon 
            wall_coordinates = polygonHandler(poly, prevpoly)
            total_wall_coordinates += wall_coordinates
            
    # Identifying Outer Walls
    outer_wall_coords = outerWallCoordinates(trajectory_kvalues)
    total_wall_coordinates += outer_wall_coords
    # trajectory = list(trajectory_kvalues[0].keys())
    
    
    # print(list(outerWallBoundingBox.exterior.coords))
    return total_wall_coordinates

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


def smoothCoordinates(wall_coordinates): #TODO complete
    ''' Ensure coordinates have the same constant (x/y) value'''
    for coord in wall_coordinates:
        pass

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
