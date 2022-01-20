import numpy as np
from bresenham import bresenham
from shapely.geometry import Point, Polygon, MultiPoint, LineString, MultiLineString
from shapely import affinity

def wallEstimation(trajectory_kvalues):
    # 1. Separate trajectory based on k-values
    kvalue_coords_map = continuousSegments(trajectory_kvalues)
    
    # 2. Determine free space in the map
    free_space_coords, new_k0_coords = findFreeSpace(trajectory_kvalues, kvalue_coords_map[0])
    kvalue_coords_map[0] += new_k0_coords
    
    # 3. Predit inner wall coordinates for ki ... kn, i = 1 to n
    wall_coords = []
    for ki in kvalue_coords_map.keys():
        if ki==0: continue
        wall_coords += iterativeAverage(ki,kvalue_coords_map[ki], kvalue_coords_map[ki-1], trajectory_kvalues)
        
    # 4. Bounding box 
    # Identifying Outer Walls
    outer_wall_coords = outerWallCoordinates(trajectory_kvalues)
    
    
    
    wall_coords += outer_wall_coords
    return free_space_coords, wall_coords

# =============================================================================
# For Step 1
def dictionaryKeySeparator(criterion, dictionary):
    # extract keys from dict whose values are equal to the criterion
    matched_values = [key for key in dictionary if dictionary[key] == criterion]
    return matched_values

def continuousSegments(trajectory_kvalues):
    k_values = list(dict.fromkeys(trajectory_kvalues[0].values()))
    trajectory_kvalues_dict = trajectory_kvalues[0] 
    # First separate based on k-value, then based on slope
    kvalue_segments = {}
    for k in k_values:
        kvalue_segments[k] = dictionaryKeySeparator(k, trajectory_kvalues_dict)        
    separated_kvalue_segments={}
    return kvalue_segments
# =============================================================================
# =============================================================================
# For Step 2
def findFreeSpace(trajectory_kvalues, k0_coords):
    free_space_coords = []
    # All points along trajectory are free space
    trajectory = list(trajectory_kvalues[0].keys())
    free_space_coords += trajectory
    
    # All points along the ray between the router --> a k0 coord are free space
    router = trajectory_kvalues[1]
    new_k0_coords = []
    for coord in k0_coords:
        line = list(bresenham(router[0],router[1],coord[0],coord[1]))
        free_space_coords += line
        new_k0_coords += line
        
    return free_space_coords, new_k0_coords
# =============================================================================
# =============================================================================
# For Step 3
def iterativeAverage(kval, ki_coords, kj_coords, trajectory_kvalues):
    router = trajectory_kvalues[1]
    kj_startpt = router
    wall_midpoints=[]
    for i in range(len(ki_coords)):
        ki_coord = ki_coords[i]
        
        
        line=list(bresenham(ki_coord[0],ki_coord[1],router[0],router[1]))

        for coord in line:
            if coord in kj_coords: 
                kj_startpt = coord
                break
        line_midpoint = midpoint(kj_startpt, ki_coord)
        wall_midpoints.append(line_midpoint)
    wall_midpoints = np.array(wall_midpoints)
    x,y = list(dict.fromkeys(wall_midpoints[:,0])), list(dict.fromkeys(wall_midpoints[:,1]))
    print('x variance:', np.var(x), 'y variance:', np.var(y))
    varx, vary = np.var(x), np.var(y)
    wall_coords = []
    ki_coords = np.array(ki_coords)
    if varx < vary:
        constant_wall_value = int(np.mean(x)) - int(np.mean(x)-min(ki_coords[:,0])+1) 
        print('x mean:',np.mean(x))
        varying_wall_values = list(y) 
        # varying_wall_values = [i for i in range(5,75)] 
        wall_coords = [(constant_wall_value, int(varying_coord)) for varying_coord in varying_wall_values]
        print(wall_coords)
        return wall_coords
    if vary < varx:
        constant_wall_value = int(np.mean(y))  - int(np.mean(y)-min(ki_coords[:,1])+1) 
        print('y mean:',np.mean(y))
        varying_wall_values = list(x) 
        # varying_wall_values = [i for i in range(5,75)] 
        wall_coords = [(int(varying_coord),constant_wall_value) for varying_coord in varying_wall_values]
        print(wall_coords)
        return wall_coords
        
    # print(np.polyfit(testrow, x,1), np.polyfit(testrow, y,1))
    print(wall_midpoints)
    print('===========================')
def midpoint(endpoint1, endpoint2):
    x_midpoint = (endpoint1[0]+endpoint2[0])/2
    y_midpoint = (endpoint1[1]+endpoint2[1])/2
    return (x_midpoint,y_midpoint)
# =============================================================================
# =============================================================================
# Step 4
def outerWallCoordinates(trajectory_kvalues, offset_distance=1.1):
    '''
        Return a list of grid coordinates corresponding to the smallest envelope encompassing the coordinates
        of the trajectory and the inner walls identified
        :type trajectory_kvalues: list with 2 elements: [dict of {coord: kval}, (routerx, routery)]
        :rtype: list
    '''
    outer_wall_coords = []
    trajectory = list(trajectory_kvalues[0].keys())
    trajectoryMultiPoint = MultiPoint(trajectory)
    outer_wall_corners = trajectoryMultiPoint.envelope
    outer_wall_corners = list(outer_wall_corners.exterior.coords)
    outer_wall_lines = []
    for i in range(len(outer_wall_corners)-1):
        point1 = outer_wall_corners[i]
        point2 = outer_wall_corners[i+1]
        linestring = LineString([point1, point2])
        outer_wall_lines+=list(linestring.coords)
    
    inner_bounding_box = Polygon(outer_wall_lines)
    inner_bounding_box_scaled = affinity.scale(inner_bounding_box, xfact=offset_distance, yfact=offset_distance)
    
    outer_wall_lines=list(inner_bounding_box_scaled.exterior.coords)
    for i in range(len(outer_wall_lines)-1):
        p1 = (int(outer_wall_lines[i][0]), int(outer_wall_lines[i][1]))
        p2 = (int(outer_wall_lines[i+1][0]), int(outer_wall_lines[i+1][1]))
        
        line = list(bresenham(p1[0],p1[1], p2[0],p2[1]))
        outer_wall_coords+=line
    return outer_wall_coords 


# =============================================================================