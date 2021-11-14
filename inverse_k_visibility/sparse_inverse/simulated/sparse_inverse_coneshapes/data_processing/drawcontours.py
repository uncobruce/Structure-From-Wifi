''' Given an image of a 2D floorplan, obtain the coordinates of its contours.'''

import cv2

class Contour:
    def __init__(self, img):
        self.img = img
        self.gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        self.erode = cv2.erode(self.gray,None, iterations=3) # replace dilate with erode to see double wall effect
        self.flipVertical = cv2.flip(self.erode, 0)
        self.contours = None

    def getContours(self): 
        # obtain countours of map, stored in self.contours
        ret, thresh = cv2.threshold(self.flipVertical, 150, 255, cv2.THRESH_BINARY)
        self.contours, hierarchy = cv2.findContours(self.flipVertical, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(self.flipVertical, self.contours, -1, (0,255,0), 3)
        return self.contours
    
    def drawContours(self):
        # draw contours of map (must call getContours first)
        imS = cv2.resize(self.img, (960, 540))   
        cv2.imshow('polygon', imS)
        cv2.waitKey()
        cv2.destroyAllWindows()


