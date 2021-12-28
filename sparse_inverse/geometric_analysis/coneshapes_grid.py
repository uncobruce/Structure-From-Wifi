''' Given a trajectory and its associated k-values, draw refined cone shapes which are completely k-visible.'''
from shapely.geometry import Point, Polygon, MultiPoint
from shapely.ops import polygonize
from shapely.ops import cascaded_union
from descartes import PolygonPatch
import numpy as np
import math

def dictionaryKeySeparator(criterion, dictionary):
    # extract keys from dict whose values are equal to the criterion
    matched_values = [key for key in dictionary if dictionary[key] == criterion]
    return matched_values

def coneshapes(trajectory_kvalues,routerpt):
    continuous_segments = continuousSegments(trajectory_kvalues)
    kvalue_coneshapes = mapConeshapes(continuous_segments, routerpt)
    kvalue_coneshapes = mapConeShapesAfterDifference(kvalue_coneshapes)
    return kvalue_coneshapes

def slope(x1, y1, x2, y2):
    if abs(x2-x1) == 0:
        return math.inf
    slope = (y2-y1)/(x2-x1)
    return slope

def separateSegments(pointslist):
    # separate a list of points into a list of segments based on slope
    segments_list=[]
    EPS = 0.2
    for point in pointslist:
        if pointslist.index(point) == 0:
            previous_point = point
            current_segment = [point]
            previous_slope = 0
            continue
        
        current_slope = slope(point[0], point[1], previous_point[0], previous_point[1])
    
        if (abs(current_slope-previous_slope) <= EPS or (current_slope== math.inf and previous_slope==math.inf)):
            current_segment.append(point)
        elif current_segment != []:
            current_segment.append(point)
            segments_list.append(current_segment)
            current_segment = [point]
        
        if pointslist.index(point) == len(pointslist)-1: # reached end of pointslist
            segments_list.append(current_segment)
            
        previous_point = point
        previous_slope = current_slope
    return segments_list

def continuousSegments(trajectory_kvalues):
    k_values = list(dict.fromkeys(trajectory_kvalues[0].values()))
    trajectory_kvalues_dict = trajectory_kvalues[0]
    
    # First separate based on k-value, then based on slope
    kvalue_segments = {}
    for k in k_values:
        kvalue_segments[k] = dictionaryKeySeparator(k, trajectory_kvalues_dict)        
    separated_kvalue_segments={}
    for k in kvalue_segments:
        separated_kvalue_segments[k] = separateSegments(kvalue_segments[k])         
    return separated_kvalue_segments


def mapConeshapes(continuous_segments, routerpt):
    kvalue_coneshapes = {}
    current_kval = 0
    for kval in continuous_segments:
        # print(kval)
        kvalue_coneshapes[current_kval] = []
        list_of_cont_segments = continuous_segments[kval]
        totalcones = []
        for cont_segment in list_of_cont_segments:
            line1 = (cont_segment[0], cont_segment[-1])
            line2 = (routerpt, cont_segment[0])
            line3 = (routerpt, cont_segment[-1])
            # print(cont_segment)
            coneregion = list(polygonize((line1,line2, line3)))
            if coneregion != []:
                cone = coneregion[0]
                totalcones.append(cone)
        kregioncones = [cone for cone in totalcones]
        # print("\n")
        
        polygon_final = cascaded_union(kregioncones)
        kvalue_coneshapes[current_kval].append(polygon_final)
        current_kval += 1
    return kvalue_coneshapes # map of kvals : coneshapes

def mapConeShapesAfterDifference(kvalue_coneshapes):
    new_kvalue_coneshapes = {}
    for i in range(len(kvalue_coneshapes)):
        kj_polys = kvalue_coneshapes[i][0]
        if i == 0:
            new_kvalue_coneshapes[0] = kj_polys
            continue
        ki_polys = kvalue_coneshapes[i-1][0]
        new_poly = kj_polys.difference(ki_polys)
        if new_poly.geom_type == 'MultiPolygon':
            polylist = list(new_poly.geoms)
            new_poly = polylist
        new_kvalue_coneshapes[i] = new_poly        
    return new_kvalue_coneshapes
    
        