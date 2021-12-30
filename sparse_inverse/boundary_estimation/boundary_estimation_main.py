''' Given a dictionary of kvalues: coneshapes, estimate wall locations and return their coordinates.'''

from shapely.geometry import Point, Polygon, MultiPoint, LineString
from shapely.ops import polygonize
from shapely.ops import cascaded_union
from descartes import PolygonPatch
import numpy as np
import math
import boundary_estimation.vertical_boundary_estimation as vertical_boundary_estimation


def boundaryEstimation(kvalue_coneshapes):
    # input: kvalue_coneshapes after geometric difference calculated 
    total_wall_coordinates = []
    for kval in kvalue_coneshapes:
        if kval == 0: continue
        poly = kvalue_coneshapes[kval]
        prevpoly = kvalue_coneshapes[kval-1] # TODO change to func for k2-k1 where there are multiple prev polys
        if type(poly) == list and kval == 1: # if multiple polys for kvalue
            for p in poly:
                wall_coordinates = polygonHandler(p, prevpoly)
                total_wall_coordinates+=wall_coordinates
        elif type(poly) == Polygon: # only one polygon
            pass #polyhandler
    return total_wall_coordinates

def slope(x1, y1, x2, y2):
    if abs(x2-x1) == 0:
        return math.inf
    slope = (y2-y1)/(x2-x1)
    return slope



def wallType(intersection):
    ''' Determine whether wall is vertical or horizontal based on intersection slope'''
    eps1, eps2, alpha = 8, 0.05, 1
    x1, y1, x2, y2 = intersection.coords[0][0], intersection.coords[0][1], intersection.coords[1][0], intersection.coords[1][1]
    m = slope(x1, y1, x2, y2)
    norm = np.linalg.norm(np.array([x2,y2])-np.array([x1,y1])) # exclude lines with endpoints too close to one another
    if (abs(m) > eps1) and norm > alpha: # If vertical wall found
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
    wall_coordinates = None   
    if intersection.geom_type == 'GeometryCollection':
        for inter in intersection:
            if inter.geom_type == 'LineString':
                wall_type = wallType(inter)
                if wall_type == 'vertical': 
                    print("Vertical wall found")
                    wall_coordinates = vertical_boundary_estimation.polygonVerticalWallCoordinates(poly, inter)   
    elif intersection.geom_type == 'LineString':
        wall_type = wallType(intersection)
        if wall_type == 'vertical': 
            print("Vertical wall found") 
            wall_coordinates = vertical_boundary_estimation.polygonVerticalWallCoordinates(poly, intersection)

    return wall_coordinates

