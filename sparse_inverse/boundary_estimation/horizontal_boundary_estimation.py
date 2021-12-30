from shapely.geometry import Point, Polygon, MultiPoint, LineString
from shapely.ops import polygonize
from shapely.ops import cascaded_union
from descartes import PolygonPatch
import numpy as np
import math

def wallVerticalDistance(intersection_edge, polygon):
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
        coordy = coord[1]
        e1y = e1[1]
        vertical_distance = int(abs(coordy-e1y))
        if closest_vertex == None or (vertical_distance < shortest_distance and vertical_distance > 0):
            closest_vertex = coord
            shortest_distance = vertical_distance
    
    return 1+shortest_distance//2 # adding 1 seems more accurate for some reason

def x_range(polygon):
    '''Obtain minimum and maximum x given a Polygon'''
    coordinates = list(polygon.exterior.coords)
    maxx = None
    minx = None
    for coord in coordinates:
        x = coord[0]
        if maxx == None or x > maxx:
            maxx = x
        if minx == None or x < minx:
            minx = x
    return int(minx), int(maxx)

def polygonHorizontalWallCoordinates(polygon, intersection):
    ''' 
    Given kj polygon and its intersection with its ki polygon, return list of coordinates matching vertical wall
    :type polygon: Polygon
    :type intersection: LineString
    :rtype: list
    '''
    intersection_edge = intersection
    distance_to_wall = wallVerticalDistance(intersection_edge, polygon)
    yStartPoint = intersection_edge.coords[0][1]
    wall_y_coordinate = int(yStartPoint + distance_to_wall)
    x_min, x_max = x_range(polygon)
    list_of_coords = []
    for i in range(x_min, x_max):
        ycoord = wall_y_coordinate
        xcoord = i
        coord = (xcoord, ycoord)
        if Point(xcoord, ycoord).within(polygon):
            list_of_coords.append(coord)
    return list_of_coords