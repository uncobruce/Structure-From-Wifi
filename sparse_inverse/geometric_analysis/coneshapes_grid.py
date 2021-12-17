''' Given a trajectory and its associated k-values, draw refined cone shapes which are completely k-visible.'''
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon, MultiPoint
from shapely.ops import polygonize
from shapely.ops import cascaded_union
from descartes import PolygonPatch
import numpy as np
import math

def coneshapes(trajectory_kvalues,routerpt):
    continuous_segments = continuousSegments(trajectory_kvalues)
    kvalue_coneshapes = mapConeshapes(continuous_segments, routerpt)
    return kvalue_coneshapes

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
    return kvalue_coneshapes

def continuousSegments(trajectory_kvalues):
    trajectoryCoordinates = list(trajectory_kvalues[0].keys())
    kvalues = list(list(dict.fromkeys(list(trajectory_kvalues[0].values()))))
    subsegments_kvalue_separated = [[] for i in range(len(kvalues))]
    
    # Separate coordinates based on k value
    for i in range(len(subsegments_kvalue_separated)):
        kval_list = [point for point in trajectoryCoordinates if trajectory_kvalues[0][point] == i] # i corresp to kvalue here
        subsegments_kvalue_separated[i] = kval_list 
    
    # Within each k-val grouping, separate into continuous segments
    current_kval = 0
    continuous_segments = {}
    EPS = 0.25 #TODO adjust EPS for erratic trajectories
    def slope(point1, point2):
        x1, y1, x2, y2 = point1[0], point1[1], point2[0], point2[1]
        if (x2-x1) == 0: return math.inf
        return (y2-y1)/(x2-x1)
    for kval_grouping in subsegments_kvalue_separated:
        print(current_kval)
    #     # print(kval_grouping)
        current_continuous_segments = []
        for i in range(len(kval_grouping)-1):
            point1, point2 = kval_grouping[i], kval_grouping[i+1]
            direction = slope(point1,point2)
            
            if i == 0 or current_continuous_segments == []:
                current_direction = direction
                if i!= 0:
                    current_continuous_segments = [kval_grouping[i-1], point1]
                else:
                    current_continuous_segments = [point1]
                previous_direction = direction
                continue
            if previous_direction == math.inf and current_direction == math.inf:
                current_continuous_segments.append(point1)
                # print(point1, point2, direction, previous_direction)

            elif abs(previous_direction-current_direction) <= EPS or abs(previous_direction-current_direction) == math.nan or abs(previous_direction-current_direction) == math.inf:
                current_continuous_segments.append(point1)
            else: # start new segment
                current_continuous_segments.append(point1)
                continuous_segments[current_kval] = current_continuous_segments
                current_continuous_segments = []
            previous_direction = direction
            print(point1, point2, direction, previous_direction, abs(previous_direction-current_direction))
        print("\n")
        current_kval +=1
    return continuous_segments