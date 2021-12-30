''' Given a dictionary of kvalues: coneshapes, estimate wall locations and return their coordinates.'''

from shapely.geometry import Point, Polygon, MultiPoint, LineString
from shapely.ops import polygonize
from shapely.ops import cascaded_union
from descartes import PolygonPatch
import numpy as np
import math


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

def wallHorizontalDistance(intersection_edge, polygon):
    '''
        :type intersection_edge: LineString
        :type polygon: Polygon being analyzed
        :rtype int: distance to wall (equal to half of x distance of closest vertex)
    '''
    coordinates = list(polygon.exterior.coords)
    intersection_edge = list(intersection_edge.coords)
    e1, e2 = intersection_edge[0], intersection_edge[1]
    shortest_distance = 100
    closest_vertex=None
    for coord in coordinates:
        if coord == e1 or coord == e2:
            continue
        coordx = coord[0]
        e1x = e1[0]
        horizontal_distance = int(abs(coordx-e1x))
        if closest_vertex == None or (horizontal_distance < shortest_distance and horizontal_distance > 0):
            closest_vertex = coord
            shortest_distance = horizontal_distance
    
    return 1+shortest_distance//2 # adding 1 seems more accurate for some reason



def y_range(polygon):
    coordinates = list(polygon.exterior.coords)
    maxy = None
    miny = None
    for coord in coordinates:
        y = coord[1]
        if maxy == None or y > maxy:
            maxy = y
        if miny == None or y < miny:
            miny = y
    return int(miny), int(maxy)

def polygonVerticalWallCoordinates(polygon, intersection):
    ''' 
    Given kj polygon and its intersection with its ki polygon, return list of coordinates matching vertical wall
    :type polygon: Polygon
    :type intersection: LineString
    :rtype: list
    '''
    intersection_edge = intersection
    distance_to_wall = wallHorizontalDistance(intersection_edge, polygon)
    xStartPoint = intersection_edge.coords[0][0]
    wall_x_coordinate = int(xStartPoint + distance_to_wall)
    y_min, y_max = y_range(polygon)
    list_of_coords = []
    for j in range(y_min, y_max):
        xcoord = wall_x_coordinate
        ycoord = j
        coord = (xcoord, ycoord)
        if Point(xcoord, ycoord).within(polygon):
            list_of_coords.append(coord)
    return list_of_coords


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
    # Wall is located along direction of intersection
    intersection = poly.intersection(prevpoly)
    wall_coordinates = None   
    if intersection.geom_type == 'GeometryCollection':
        for inter in intersection:
            if inter.geom_type == 'LineString':
                wall_type = wallType(inter)
                if wall_type == 'vertical': # If vertical wall found
                    print("Vertical wall found")
                    wall_coordinates = polygonVerticalWallCoordinates(poly, intersection)
                    
    elif intersection.geom_type == 'LineString':
        wall_type = wallType(intersection)
        if wall_type == 'vertical': # Vertical wall found
            print("Vertical wall found") 
            wall_coordinates = polygonVerticalWallCoordinates(poly, intersection)
       
                

    return wall_coordinates

