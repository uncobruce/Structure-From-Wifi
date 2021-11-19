import cv2
import numpy as np
from shapely.geometry import Polygon 
import data_processing.drawcontours as drawcontours
import data_processing.kvisibility_algorithm as kvisibility_algorithm
import grid_mapping.grid_map as grid_map
import data_processing.associate_traj_kvals as associate_traj_kvals
import geometric_analysis.coneshapes as coneshapes

class Floorplan:
    def __init__(self, floorplan_img_path):
        self.floorplan = cv2.imread(floorplan_img_path)
        self.map_contour = drawcontours.contours(self.floorplan)
        self.map_contour = np.squeeze(self.map_contour)
        self.floorplanPolygon = Polygon(self.map_contour)
        
    def getMapContour(self):
        return self.map_contour
    
    def getAxisLimits(self):
        polygon_coordinates = np.array(list(self.floorplanPolygon.exterior.coords))
        xmin, xmax, ymin, ymax = min(polygon_coordinates[:,0]), max(polygon_coordinates[:,0]), min(polygon_coordinates[:,1]), max(polygon_coordinates[:,1])
        print(f"xmin: {xmin}, xmax: {xmax}, ymin: {ymin} ymax: {ymax}")
        return ((xmin, xmax), (ymin,ymax))
    
# Part 1: Obtaining trajectory-kvals-routerpt object
# =========================================================
# Initialize floorplan input
floorplan_img_path = "floorplans/testroom.png"
floorplan = Floorplan(floorplan_img_path)
print(floorplan.getMapContour())
print(floorplan.getAxisLimits())

# Obtain map contours
#map_contour = np.array(drawcontours.contours(floorplan))

# floorplan_x_max, floorplan_x_min, floorplan_y_max, floorplan_y_min = max(map_contour[:,0]), min(map_contour[:,0]), max(map_contour[:,1]), min(map_contour[:,1])    

# # Obtain k-visibility plot and router point
# routerpoint, unscaled_axis_limits, kvaluescolordict = kvisibility_algorithm.plotKVisRegion(map_contour, showPlot=False)
# facecolors=['red','yellow','blue','green','orange', 'magenta', 'navy', 'teal', 'tan', 'lightsalmon','lightyellow','coral','rosybrown']
# kvisibility_map_image = cv2.imread('data_processing/kvis_plot.png')

# # Initialize grid map
# gridWidth, gridHeight = 80, 80
# gridMap = grid_map.GridMap()

# # Obtain k-visibility gridmap
# kvis_gridmap = gridMap.plotKVisibilityMap(kvisibility_map_image, showPlot=False)


# # Obtain traj-kvals data object scaled to gridmap
# trajectory_endpts_path = "random_trajectories/traj_1.txt" 
# kvisplot_path = "data_processing/kvis_plot.png"
# trajectoryObject = associate_traj_kvals.trajectoryObject(trajectory_endpts_path, kvisplot_path, gridWidth, gridHeight,routerpoint, unscaled_axis_limits, kvaluescolordict, kvis_gridmap)
# trajectory_kvalues = trajectoryObject.getTrajectoryKValuesObject()
# # =========================================================

# # Phase II: obtaining refined cone shapes
# # =========================================================
# # Plot trajectory and ground truth on grid map
# gridMap.plotFloorplanGroundTruth(floorplan)
# gridMap.plotGrid(kvis_gridmap)
# gridMap.plotTrajectory(trajectory_kvalues)


# coneshapes_gridmap, rgb = coneshapes.getRefinedConeShapes(trajectory_kvalues, gridWidth, gridHeight, facecolors, kvaluescolordict)
# a = kvis_gridmap[1][0]
# kvis_gridmap[1][0] = (255,255,255)