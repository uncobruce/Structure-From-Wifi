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
mapimg = cv2.imread("floorplans/testroom.png")
map1 = mapInput(mapimg)

# Obtain map contours
map_contour = drawcontours.Contour(mapimg)
map_contour.getContours()
