''' Given a dictionary of kvalues: coneshapes, estimate wall locations and return their coordinates.'''

from shapely.geometry import Point, Polygon, MultiPoint, LineString
from shapely.ops import polygonize
from shapely.ops import cascaded_union
from descartes import PolygonPatch
import numpy as np
import math


def boundaryEstimation(kvalue_coneshapes):
    # input: kvalue_coneshapes after geometric difference calculated 
    wall_coordinates = None
    for kval in kvalue_coneshapes:
        if kval == 0: continue
        poly = kvalue_coneshapes[kval]
        prevpoly = kvalue_coneshapes[kval-1] # TODO change to func for k2-k1 where there are multiple prev polys
        if type(poly) == list and kval == 1: # if multiple polys for kvalue
            # for p in poly:
            wall_coordinates = polygonHandler(poly[0], prevpoly)
        elif type(poly) == Polygon: # only one polygon
            pass #polyhandler
    return wall_coordinates

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

def polygonVerticalWallCoordinates(polygon, x_coordinate, y_min, y_max):
    list_of_coords = []
    for j in range(y_min, y_max):
        xcoord = x_coordinate
        ycoord = j
        coord = (xcoord, ycoord)
        if Point(xcoord, ycoord).within(polygon):
            list_of_coords.append(coord)
    return list_of_coords

def polygonHandler(poly, prevpoly):
    ''' :type poly: current kj Polygon (k_i-1) polygon being analyzed for walls
        :type prevpoly: ki Polygon being compared with kj polygon
        :rtype: wall coordinates 
    '''
    wall_coordinates = None
    eps1, eps2, alpha = 8, 0.05, 1
    intersection = poly.intersection(prevpoly)
    if intersection.geom_type == 'GeometryCollection':
        for inter in intersection:
            if inter.geom_type == 'LineString':
                x1, y1, x2, y2 = inter.coords[0][0], inter.coords[0][1], inter.coords[1][0], inter.coords[1][1]
                m = slope(x1, y1, x2, y2)
                norm = np.linalg.norm(np.array([x2,y2])-np.array([x1,y1]))
                if (abs(m) > eps1) and norm > alpha: # If vertical wall found
                    print("Vertical wall found")
                    intersection_edge = inter
                    distance_to_wall = wallHorizontalDistance(intersection_edge, poly)
                    wall_x_coordinate = int(x1 + distance_to_wall)
                    y_min, y_max = y_range(poly)
                    wall_coordinates = polygonVerticalWallCoordinates(poly, wall_x_coordinate, y_min, y_max)
                    
    elif intersection.geom_type == 'LineString':
        x1, y1, x2, y2 = intersection.coords[0][0], intersection.coords[0][1], intersection.coords[1][0], intersection.coords[1][1]
        m = slope(x1, y1, x2, y2)
        norm = np.linalg.norm(np.array([x2,y2])-np.array([x1,y1]))
        if (abs(m) > eps1) and norm > alpha: # Vertical wall found
            print("Vertical wall found")
       
                
    print("\n")
    return wall_coordinates

