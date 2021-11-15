''' Initialize a gridmap and plot coordinates in a grid format.'''
import numpy as np 
import cv2

class GridMap:
    def __init__(self, refined_polygons_list, trajectory_object, desired_height=80, desired_width=80):
        self.gridmap = np.zeros(desired_width*desired_height)
        self.gridmap = self.gridmap.reshape((desired_width, desired_height))
        self.gridmap[self.gridmap == 0] = 0.5
        self.desired_height, self.desired_width = desired_height, desired_width
        

    def plotFloorplanGroundTruth(self, ground_truth_image):
        ''' Draw ground truth map scaled to desired grid size. 
            Cell colour = 1: wall; Cell colour = 0: free space'''
        # Get input size
        height, width = ground_truth_image.shape[:2]
        # Desired "pixelated" size
        w, h = (500, 500)
        # Resize input to "pixelated" size
        temp = cv2.resize(ground_truth_image, (w, h), interpolation=cv2.INTER_LINEAR)
        # Initialize output image
        output = cv2.resize(temp, (self.desired_width, self.desired_height), interpolation=cv2.INTER_NEAREST)
        # Obtain coordinates of map points in image
        mapCoordinates = []
        for i in range(self.desired_height):
            for j in range(self.desired_width):
                pixel = output[i][j]
                if pixel[0] != 255:
                    output[i][j][0], output[i][j][1], output[i][j][2] = 0,0,0
                    mapCoordinates.append((j,-i)) 
        # Add map components (walls and obstacles) to grid map
        mapCoordinates.sort()
        mapCoordinates=np.array(mapCoordinates)  
        for coords in mapCoordinates:
            mapx, mapy = coords[0],coords[1]
            self.gridmap[mapy-5][mapx+5] = 1
        return self.gridmap
    
    
    
    
    def plotTrajectory():
        pass