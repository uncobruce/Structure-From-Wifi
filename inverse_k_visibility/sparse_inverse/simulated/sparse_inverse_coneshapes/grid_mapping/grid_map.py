''' Initialize a gridmap and plot coordinates in a grid format.'''
import numpy as np 

class GridMap:
    def __init__(self, refined_polygons_list, trajectory_object, desired_height=80, desired_width=80):
        self.gridmap = np.zeros(desired_width*desired_height)
        self.gridmap = self.gridmap.reshape((desired_width, desired_height))
        self.gridmap[self.gridmap == 0] = 0.5
        return self.gridmap

