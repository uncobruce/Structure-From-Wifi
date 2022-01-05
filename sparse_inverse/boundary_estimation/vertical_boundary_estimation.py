from shapely.geometry import Point, Polygon, MultiPoint, LineString
from shapely.ops import polygonize
from shapely.ops import cascaded_union
from descartes import PolygonPatch
import numpy as np
import math

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
    
    return shortest_distance//2 # adding 1 seems more accurate for some reason



def y_range(polygon):
    '''Obtain minimum and maximum y given a Polygon'''
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
