import cv2
import sys
import data_processing.drawcontours as drawcontours
import data_processing.kvisibility_algorithm as kvisibility_algorithm
import grid_mapping.grid_map as grid_map
import data_processing.associate_traj_kvals as associate_traj_kvals
import geometric_analysis.coneshapes as coneshapes

class mapInput:
    def __init__(self, mapimage):
        self.mapimage = mapimage
    
    def displayMapInput(self):
        cv2.imshow('map', self.mapimage)
        cv2.waitKey()
        cv2.destroyAllWindows()

# Phase I: obtaining trajectory-kvals-routerpt object
# =========================================================
# Initialize map input
map_img = cv2.imread("floorplans/testroom.png")
map1 = mapInput(map_img)


# Obtain map contours
map_contour = drawcontours.Contour(map_img)
contours = map_contour.getContours()


# Obtain k-visibility plot and router point
routerpoint, unscaled_axis_limits, kvaluescolordict = kvisibility_algorithm.plotKVisRegion(contours, showPlot=False)
facecolors=['red','yellow','blue','green','orange', 'magenta', 'navy', 'teal', 'tan', 'lightsalmon','lightyellow','coral','rosybrown']
kvisibility_map_image = cv2.imread('data_processing/kvis_plot.png')

# Initialize grid map
gridWidth, gridHeight = 80, 80
gridMap = grid_map.GridMap()

# Obtain k-visibility gridmap
kvis_gridmap = gridMap.plotKVisibilityMap(kvisibility_map_image, showPlot=False)



# Obtain traj-kvals data object scaled to gridmap
trajectory_endpts_path = "random_trajectories/traj_1.txt" 
kvisplot_path = "data_processing/kvis_plot.png"
trajectoryObject = associate_traj_kvals.trajectoryObject(trajectory_endpts_path, kvisplot_path, gridWidth, gridHeight,routerpoint, unscaled_axis_limits, kvaluescolordict, kvis_gridmap)
trajectory_kvalues = trajectoryObject.getTrajectoryKValuesObject()
# =========================================================

# Phase II: obtaining refined cone shapes
# =========================================================
# Plot trajectory and ground truth on grid map
# gridMap.plotFloorplanGroundTruth(map_img)
gridMap.plotGrid(kvis_gridmap)
gridMap.plotTrajectory(trajectory_kvalues)


coneshapes_gridmap, rgb = coneshapes.getRefinedConeShapes(trajectory_kvalues, gridWidth, gridHeight, facecolors, kvaluescolordict)
# gridMap.plotGrid(coneshapes_gridmap)
a = kvis_gridmap[1][0]
kvis_gridmap[1][0] = (255,255,255)