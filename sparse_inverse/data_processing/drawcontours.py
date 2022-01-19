''' Given an image of a 2D floorplan, draw the coordinates of its contours.'''

import cv2
import numpy as np
def contours(floorplan_image): 
    # Input: cv2 floorplan image
    # Output: contour coordinates
    gray = cv2.cvtColor(floorplan_image, cv2.COLOR_BGR2GRAY)
    erode = cv2.erode(gray,None, iterations=3)
    
    # image = cv2.bitwise_not(gray)
    # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (200,200))
    
    # result = 255 - cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel, iterations=1)
    
    
    flipVertical = cv2.flip(erode, 0)
    ret, thresh = cv2.threshold(flipVertical, 150, 255, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(flipVertical, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(flipVertical, contours, -1, (0,255,0), 3)
    imS = cv2.resize(erode, (960, 540))   
    # cv2.imshow('polygon', imS)
    # cv2.waitKey()
    # cv2.destroyAllWindows()
    #cv2.imwrite('C:/Users/jzala/Documents/GitHub/Structure-From-Wifi/sparse_inverse/floorplans/floorplan_image_closed_gaps.jpg', result)

    return contours

