import cv2

#warnings.filterwarnings("ignore", category=DeprecationWarning) 

# Convert polygon image to grayscale
img = cv2.imread("testroom.png") # ensure image is in same directory
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
canny = cv2.Canny(gray, 120, 255, 1)
dilate = cv2.dilate(gray,None, iterations=3)
erode = cv2.erode(gray,None, iterations=6) # replace dilate with erode to see double wall effect
flipVertical = cv2.flip(dilate, 0)


ret, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

contours, hierarchy = cv2.findContours(flipVertical, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
cv2.drawContours(img, contours, -1, (0,255,0), 3)



# imS = cv2.resize(img, (960, 540))   
# cv2.imshow('polygon', imS)
# cv2.waitKey()
# cv2.destroyAllWindows()
