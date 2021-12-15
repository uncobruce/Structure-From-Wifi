import cv2
import numpy as np
from shapely.geometry import Polygon 
import data_processing.drawcontours as drawcontours
import data_processing.kvisibility_algorithm as kvisibility_algorithm
import grid_mapping.grid_map as grid_map
import data_processing.associate_traj_kvals as associate_traj_kvals
import geometric_analysis.coneshapes_grid as coneshapes

class Floorplan:
    def __init__(self, floorplan_img_path):
        self.image = cv2.imread(floorplan_img_path)
        self.map_contour = drawcontours.contours(self.image)
        self.map_contour = np.squeeze(self.map_contour)
        self.floorplanPolygon = Polygon(self.map_contour)
        
    def mapContour(self):
        return self.map_contour
    
    def axisLimits(self):
        polygon_coordinates = np.array(list(self.floorplanPolygon.exterior.coords))
        xmin, xmax, ymin, ymax = min(polygon_coordinates[:,0]), max(polygon_coordinates[:,0]), min(polygon_coordinates[:,1]), max(polygon_coordinates[:,1])
        return (xmin, xmax, ymin,ymax)
    

    
# Part 1: Data Processing and Initialization
# =========================================================
# Initialize floorplan input
floorplan_img_path = "floorplans/testroom.png"
floorplan = Floorplan(floorplan_img_path)

# Obtain map contours
map_contour = np.array(floorplan.mapContour())

# floorplan_x_max, floorplan_x_min, floorplan_y_max, floorplan_y_min = max(map_contour[:,0]), min(map_contour[:,0]), max(map_contour[:,1]), min(map_contour[:,1])    


# Obtain k-visibility plot and router point
routerpoint, unscaled_axis_limits, kvaluescolordict = kvisibility_algorithm.plotKVisRegion(map_contour, showPlot=False)
facecolors=['red','yellow','blue','green','orange', 'magenta', 'navy', 'teal', 'tan', 'lightsalmon','lightyellow','coral','rosybrown']
kvisibility_map_image = cv2.imread('data_processing/kvis_plot.png')
floorplan_x_max, floorplan_y_max = unscaled_axis_limits[0],unscaled_axis_limits[1]
# Initialize grid map
gridWidth, gridHeight = 80, 80
gridMap = grid_map.GridMap(floorplan.image)

# Obtain k-visibility gridmap
kvis_gridmap = gridMap.plotKVisibilityMap(kvisibility_map_image, showPlot=False)

# Obtain traj-kvals data object scaled to gridmap
trajectory_endpts_path = "random_trajectories/traj_1.txt" 
kvisplot_path = "data_processing/kvis_plot.png"
trajectoryObject = associate_traj_kvals.trajectoryObject(trajectory_endpts_path, kvisplot_path, gridWidth, gridHeight, routerpoint, unscaled_axis_limits, kvaluescolordict, kvis_gridmap)
trajectory_kvalues = trajectoryObject.getTrajectoryKValuesObject()

# Scale router point to grid map size
routery, routerx = int((gridHeight)*routerpoint[0]/floorplan_y_max), int((gridWidth)*routerpoint[1]/floorplan_x_max)
scaled_routerpoint = (routerx, routery)

# Plot trajectory and ground truth on grid map
# gridMap.plotFloorplanGroundTruth(floorplan.image)
# gridMap.plotGrid(kvis_gridmap)
# gridMap.plotTrajectory(trajectory_kvalues, showPlot=False)


# Phase II: Geometric Analysis
# =========================================================
coneshapes = coneshapes.coneshapes(trajectory_kvalues, scaled_routerpoint)

# Phase III: Occupancy Grid Mapping
# =========================================================
gridMap.updateOccupancyGrid(coneshapes, facecolors, showPlot=True, showGroundTruth=False)
# kvalues = list(coneshapes.keys())
# kvalues.reverse()
# for k in kvalues:
#     k_coneshapes = coneshapes[k]
    
# gridmap = gridMap.gridmap
# gridmap = np.stack((gridmap,)*3, axis=-1)
# gridmap[10][10] = (0,0,0)

# print(type(gridmap))
# print(gridmap[10])
# gridMap.plotGrid(gridmap)

# poly = coneshapes[0][0]
# point = Point(10,10)
# print(poly.contains(Point(30,30)))