''' Given a dictionary of kvalues: coneshapes, estimate wall locations and return their coordinates.'''

from shapely.geometry import Point, Polygon, MultiPoint
from shapely.ops import polygonize
from shapely.ops import cascaded_union
from descartes import PolygonPatch
import numpy as np
import math


def slope(x1, y1, x2, y2):
    if abs(x2-x1) == 0:
        return math.inf
    slope = (y2-y1)/(x2-x1)
    return slope

def multiPolygonWallSlope(multipolys, ki):
    k_j_polygons = list(multipolys.geoms)
    wall_slope = None
    for kj in k_j_polygons:    
        intersection = kj.intersection(ki)
        if intersection.geom_type == 'LineString':
            x1, y1 = intersection.coords[0][0], intersection.coords[0][1]
            x2, y2 = intersection.coords[1][0], intersection.coords[1][1]
            m = slope(x1, y1, x2, y2)
            if wall_slope == math.inf or wall_slope == 0:
                continue
            elif m == math.inf or m == 0:
                wall_slope = m
            elif wall_slope == None or abs(m) > wall_slope:
                wall_slope = m
        elif intersection.geom_type == 'GeometryCollection':
            for inter in intersection:
                if inter.geom_type == 'LineString':
                    x1, y1 = inter.coords[0][0], inter.coords[0][1]
                    x2, y2 = inter.coords[1][0], inter.coords[1][1]
                    m = slope(x1, y1, x2, y2)
                    if wall_slope == math.inf or wall_slope == 0:
                        continue
                    elif m == math.inf or m == 0:
                        wall_slope = m
                    elif wall_slope == None or abs(m) > wall_slope:
                        wall_slope = m    
    if wall_slope == math.inf or abs(wall_slope) > 35:
        wall_slope = 'vertical'
    return wall_slope
    
def getHorizMidPoint(polygon):
    pass # get polygon midpoint from router-most coord to closest x coord

def closestXPointtoRouter(midpoints):
    smallest_distance = 0
    midpoint = None
    return midpoint
def multiPolygonMidPointHandler(multipolys, wall_slope):
    k_j_polygons = list(multipolys.geoms)
    if wall_slope == 'vertical':
        midpoints=[]
        for kj in k_j_polygons:
            midpoint = getHorizMidPoint(kj)
            midpoints.append(midpoint)
        midpoint = closestXPointtoRouter(midpoints)

def multiPolygonHorizWallEstimator(wallHorizMidPoint, multipolys):
    k_j_polygons = list(multipolys.geoms)    
    # plot wall along all y coords within poly at same wallhorizmidpoint

def wallCoordinates(coneshapes_dict):
    ki = coneshapes_dict[0][0]
    kj = coneshapes_dict[1][0]
    difference = kj.difference(ki)
    if difference.geom_type == 'MultiPolygon':
        wall_slope = multiPolygonWallSlope(difference, ki)
        wallHorizMidPoint = multiPolygonMidPointHandler(difference, wall_slope)
        wallEstimation = multiPolygonHorizWallEstimator(wallHorizMidPoint, difference)




def intersectionType(intersection):
    return intersection