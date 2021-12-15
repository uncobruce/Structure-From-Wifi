''' Given a trajectory and its associated k-values, draw refined cone shapes which are completely k-visible.'''
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon, MultiPoint
from shapely.ops import polygonize
from shapely.ops import cascaded_union
from descartes import PolygonPatch
import math

def coneshapes(trajectory_kvalues, routerpt):
    continuous_segments = continuousSegments(trajectory_kvalues)
    print(routerpt)
    
    
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
    EPS = 0.1 #TODO adjust EPS for erratic trajectories
    def slope(point1, point2):
        x1, y1, x2, y2 = point1[0], point1[1], point2[0], point2[1]
        if (x2-x1) == 0: return math.inf
        return (y2-y1)/(x2-x1)
    for kval_grouping in subsegments_kvalue_separated:
        continuous_segments[current_kval] = [] # initialize list of continuous segments for current k value group
        current_continuous_segments = []
        for i in range(len(kval_grouping)-1):
            point1, point2 = kval_grouping[i], kval_grouping[i+1]
            direction = slope(point1,point2)
            if i == 0 or current_continuous_segments == []:
                current_direction = direction
                current_continuous_segments = [point1]
                previous_direction = direction
                continue
            if previous_direction == math.inf and current_direction == math.inf:
                current_continuous_segments.append(point1)
            elif abs(previous_direction-current_direction) <= EPS:
                current_continuous_segments.append(point1)
            else:
                continuous_segments[current_kval].append(current_continuous_segments)
                current_continuous_segments = []
            previous_direction = direction
            
        current_kval +=1
    return continuous_segments