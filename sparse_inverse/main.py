import cv2
import numpy as np
from shapely.geometry import Polygon 
import data_processing.drawcontours as drawcontours
import data_processing.kvisibility_algorithm as kvisibility_algorithm
import data_processing.drawcontours as drawcontours
import grid_mapping.grid_map as grid_map
import data_processing.associate_traj_kvals as associate_traj_kvals
import data_processing.square_trajectory as square_trajectory
import geometric_analysis.coneshapes_grid as coneshapes
import boundary_estimation.boundary_estimation_main as boundary_estimation
import boundary_estimation.ray_drawing as ray_drawing
class Floorplan:
    def __init__(self, floorplan_img_path):
        self.image = cv2.imread(floorplan_img_path)
        self.map_contour = drawcontours.contours(self.image)
        self.map_contour = np.squeeze(self.map_contour)
        self.floorplanPolygon = Polygon(self.map_contour)
        # cv2.imshow('polygon', result)
        # cv2.waitKey()
        # cv2.destroyAllWindows()
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
routerpoint, unscaled_axis_limits, kvaluescolordict = kvisibility_algorithm.plotKVisRegion(map_contour, showPlot=False, showBorders=False,saveImage=False)
facecolors=['red','yellow','blue','green','orange', 'magenta', 'navy', 'teal', 'tan', 'lightsalmon','lightyellow','coral','rosybrown']
kvisibility_map_image = cv2.imread('data_processing/kvis_plot.png')
floorplan_x_max, floorplan_y_max = unscaled_axis_limits[0],unscaled_axis_limits[1]
# Initialize grid map
gridWidth, gridHeight = 80, 80
gridMap = grid_map.GridMap(floorplan.image)

# # Obtain k-visibility gridmap
kvis_gridmap = gridMap.plotKVisibilityMap(kvisibility_map_image, showPlot=True)
gridMap.plotFloorplanGroundTruth()

# Obtain traj-kvals data object scaled to gridmap
trajectory_endpts_path = "random_trajectories/traj_3.txt" 
kvisplot_path = "data_processing/kvis_plot.png"
trajectoryObject = associate_traj_kvals.trajectoryObject(trajectory_endpts_path, kvisplot_path, gridWidth, gridHeight, routerpoint, unscaled_axis_limits, kvaluescolordict, kvis_gridmap)
trajectory_kvalues = trajectoryObject.getTrajectoryKValuesObject()
gridMap.plotGrid(kvis_gridmap)

gridMap.plotTrajectory(trajectory_kvalues)
# =============================================================================
# Ray Drawing Algorithm
# =============================================================================
estimatedMap = grid_map.GridMap('')
free_space_coords, wall_coords = ray_drawing.wallEstimation(trajectory_kvalues)

estimatedMap.plotFreeSpace(free_space_coords)
estimatedMap.plotWallCoordinates(wall_coords)

# estimatedMap.plotWallCoordinates(wall_coords)
