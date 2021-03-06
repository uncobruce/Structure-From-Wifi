import cv2
import numpy as np
from shapely.geometry import Polygon 
import data_processing.drawcontours as drawcontours
import data_processing.kvisibility_algorithm as kvisibility_algorithm
import grid_mapping.grid_map as grid_map
import data_processing.associate_traj_kvals as associate_traj_kvals
import geometric_analysis.coneshapes_grid as coneshapes
import boundary_estimation.boundary_estimation_main as boundary_estimation

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

gridMap.plotGrid(kvis_gridmap)




# # Phase II: Geometric Analysis
# # =========================================================
cont_segs = coneshapes.continuousSegments(trajectory_kvalues)
coneshapes = coneshapes.coneshapes(trajectory_kvalues, trajectoryObject.routerCoords)
# coneshapes_grid = gridMap.plotKValueConeshapes(coneshapes, facecolors, showPlot=True, showGroundTruth=False) # show coneshapes plotted on gridmap
gridMap.plotFloorplanGroundTruth()



# Phase III: Boundary Estimation
# =========================================================
# # Initialize new gridmap for estimated wall coordinates
estimatedMap = grid_map.GridMap('')
estimatedMap.plotTrajectory(trajectory_kvalues)

# # Estimate wall coordinates
# wall_coordinates = boundary_estimation.boundaryEstimation(coneshapes, trajectory_kvalues)
