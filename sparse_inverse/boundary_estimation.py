''' Given a dictionary of kvalues: coneshapes, estimate wall locations and return their coordinates.'''

from shapely.geometry import Point, Polygon, MultiPoint, LineString
from shapely.ops import polygonize
from shapely.ops import cascaded_union
from descartes import PolygonPatch
import numpy as np
import math


def boundaryEstimation(kvalue_coneshapes, router):
    # input: kvalue_coneshapes after geometric difference calculated
    # print(kvalue_coneshapes)
    for kval in kvalue_coneshapes:
        if kval == 0: continue
        poly = kvalue_coneshapes[kval]
        prevpoly = kvalue_coneshapes[kval-1] # TODO change to func for k2-k1 where there are multiple prev polys
        if type(poly) == list and kval == 1: # multiple polys for kvalue
            #for p in poly:
            return poly[0], prevpoly
            polygonHandler(poly[0], prevpoly, router)
        elif type(poly) == Polygon: # only one polygon
            pass #polyhandler
        
    


def slope(x1, y1, x2, y2):
    if abs(x2-x1) == 0:
        return math.inf
    slope = (y2-y1)/(x2-x1)
    return slope

def polygonHandler(poly, prevpoly, router):
    ''' :type poly: current kj Polygon (k_i-1) polygon being analyzed for walls
        :type prevpoly: ki Polygon being compared with kj polygon
        :rtype: wall coordinates 
        '''
    eps1, eps2, alpha = 4.5, 0.05, 1
    coordinates = list(poly.exterior.coords)
    edges = [(coordinates[i], coordinates[i+1]) for i in range(len(coordinates)-1)]
    # For each edge: 
    closest_edge_to_router=None # edge bordering ki poly
    shortest_dist_to_router = 100
    
    for edge in edges:   
        # Calculate slope
        p1, p2 = edge[0], edge[1]
        m = slope(int(p1[0]), int(p1[1]), int(p2[0]), int(p2[1]))
        norm = np.linalg.norm(np.array(p2)-np.array(p1)) # points too close are disregarded
        dist_to_router = np.linalg.norm(np.array(p1)-np.array(router))
        
        # USE THE INTERSECTION 
        
        poly_intersects_prevpoly = poly.intersects(prevpoly)
        # If there is a vertical wall, send to vertical wall handler
        if abs(m) >= eps1 and norm > alpha:
            if (closest_edge_to_router == None or dist_to_router < shortest_dist_to_router):
                shortest_dist_to_router = dist_to_router
                closest_edge_to_router = edge
                wall_slope = 'vertical'
                print(p1,p2, wall_slope)
                print(poly, prevpoly)
                # send to vertical wall handler
                
        # If there is a horizontal wall, send to horiz wall handler
        elif abs(m) <= eps2 and norm > alpha:
            pass
                
    return poly, prevpoly
            
        

        
            
        
            # Append all wall coords to a list
    print("\n")
    

