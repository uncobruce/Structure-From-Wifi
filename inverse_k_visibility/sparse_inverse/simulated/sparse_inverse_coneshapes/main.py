import cv2
import sys
import data_processing.drawcontours as drawcontours
import data_processing.kvisibility_algorithm as kvisibility_algorithm
import grid_mapping.grid_map as grid_map

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
routerpoint = kvisibility_algorithm.plotKVisRegion(contours)


# Initialize grid map
gridWidth, gridHeight = 80, 80
gridMap = grid_map.GridMap([], None)
gridMap.plotFloorplanGroundTruth(map_img)
# Obtain traj-kvals data object scaled to gridmap


# =========================================================