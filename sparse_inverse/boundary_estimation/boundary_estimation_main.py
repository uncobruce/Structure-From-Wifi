''' Given a dictionary of kvalues: coneshapes, estimate wall locations and return their coordinates.'''

from shapely.geometry import Point, Polygon, MultiPoint, LineString
from shapely.ops import polygonize
from shapely.ops import cascaded_union
from descartes import PolygonPatch
import numpy as np
import math
import boundary_estimation.vertical_boundary_estimation as vertical_boundary_estimation 
import boundary_estimation.horizontal_boundary_estimation as horizontal_boundary_estimation 

def boundaryEstimation(kvalue_coneshapes):
    # input: kvalue_coneshapes after geometric difference calculated 
    total_wall_coordinates = []
    for kval in kvalue_coneshapes:
        if kval == 0: continue
        poly = kvalue_coneshapes[kval]
        prevpoly = previousPolygon(kvalue_coneshapes[kval-1], poly) 
        if type(poly) == list: # if multiple polys for kvalue
            for p in poly:
                wall_coordinates = polygonHandler(p, prevpoly)
                total_wall_coordinates+=wall_coordinates
        if type(poly) == Polygon: # only one polygon #TODO change back to elif
            wall_coordinates = polygonHandler(poly, prevpoly)
            total_wall_coordinates += wall_coordinates
    return total_wall_coordinates

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
    print(m, intersection)
    
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

