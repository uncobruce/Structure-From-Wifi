import cv2
import skimage
from skimage import data, io, filters, exposure
#warnings.filterwarnings("ignore", category=DeprecationWarning) 

# Convert polygon image to grayscale
img = cv2.imread("floorplans/testroom.png") # ensure image is in same directory
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray, (0,0), sigmaX=3, sigmaY=3, borderType = cv2.BORDER_DEFAULT)
result = skimage.exposure.rescale_intensity(blur, in_range=(127.5,255), out_range=(0,255))



dilate = cv2.dilate(gray,None, iterations=3)
erode = cv2.erode(gray,None, iterations=3) # replace dilate with erode to see double wall effect


flipVertical = cv2.flip(erode, 0)

ret, thresh = cv2.threshold(flipVertical, 150, 255, cv2.THRESH_BINARY)
contours, hierarchy = cv2.findContours(flipVertical, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
cv2.drawContours(flipVertical, contours, -1, (0,255,0), 3)



# imS = cv2.resize(img, (960, 540))   
# cv2.imshow('polygon', imS)
# cv2.waitKey()
# cv2.destroyAllWindows()


