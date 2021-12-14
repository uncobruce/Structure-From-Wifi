''' Given a trajectory and its associated k-values, draw refined cone shapes which are completely k-visible.'''
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon, MultiPoint
from shapely.ops import polygonize
from shapely.ops import cascaded_union
from descartes import PolygonPatch


def continuousSegments(trajectory_kvalues):
    trajectoryCoordinates = list(trajectory_kvalues[0].keys())
    kvalues = list(list(dict.fromkeys(list(trajectory_kvalues[0].values()))))
    subsegments_kvalue_separated = [[] for i in range(len(kvalues))]
    
    # Separate coordinates based on k value
    for i in range(len(subsegments_kvalue_separated)):
        kval_list = [point for point in trajectoryCoordinates if trajectory_kvalues[0][point] == i] # i corresp to kvalue here
        subsegments_kvalue_separated[i] = kval_list
    print(subsegments_kvalue_separated[0])
        