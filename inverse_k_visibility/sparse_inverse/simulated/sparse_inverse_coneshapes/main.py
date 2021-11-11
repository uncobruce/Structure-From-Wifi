import cv2
import data_processing.drawcontours as drawcontours

class mapInput:
    def __init__(self, mapimage):
        self.mapimage = mapimage
    
    def displayMapInput(self):
        cv2.imshow('map', self.mapimage)
        cv2.waitKey()
        cv2.destroyAllWindows()
        
# Initialize map input
map_img = cv2.imread("floorplans/testroom.png")
map1 = mapInput(map_img)

# Obtain map contours
map_contour = drawcontours.Contour(map_img)
map_contour.getContours()

# Obtain k-visibility plot 

# Obtain random trajectory

# Associate k-values with trajectory coordinates
