''' Initialize a gridmap and plot coordinates in a grid format.'''
import numpy as np 
import cv2
import matplotlib.pyplot as plt
from matplotlib import colors

from shapely.geometry import Point, Polygon, MultiPoint
from shapely.ops import polygonize
from shapely.ops import cascaded_union
from descartes import PolygonPatch
class GridMap:
    def __init__(self, ground_truth_image, desired_height=80, desired_width=80):
        self.gridmap = np.zeros(desired_width*desired_height)
        self.gridmap = self.gridmap.reshape((desired_width, desired_height))
        self.gridmap[self.gridmap == 0] = 0.5
        self.desired_height, self.desired_width = desired_height, desired_width
        self.ground_truth_image = ground_truth_image

    def plotFloorplanGroundTruth(self):
        ''' Draw ground truth map scaled to desired grid size. 
            Cell colour = 1: wall; Cell colour = 0: free space'''
        # Get input size
        height, width = self.ground_truth_image.shape[:2]
        # Desired "pixelated" size
        w, h = (500, 500)
        # Resize input to "pixelated" size
        temp = cv2.resize(self.ground_truth_image, (w, h), interpolation=cv2.INTER_LINEAR)
        # Initialize output image
        output = cv2.resize(temp, (self.desired_width-10, self.desired_height-10), interpolation=cv2.INTER_NEAREST)
        # Obtain coordinates of map points in image
        mapCoordinates = []
        for i in range(self.desired_height-10):
            for j in range(self.desired_width-10):
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
        self.plotGrid(self.gridmap)
        return self.gridmap
    
    def resetGrid(self):
        for i in range(len(self.gridmap)):
            for j in range(len(self.gridmap)):
                self.gridmap[i][j] = 0.5
    
    def plotGrid(self, gridmap):  
        fig, ax = plt.subplots()
        ax.imshow(gridmap, cmap="Greys",origin="lower", vmax=1)
        ax.set_xticks(np.arange(self.desired_height+1)-0.5, minor=True)
        ax.set_yticks(np.arange(self.desired_width+1)-0.5, minor=True)
        ax.grid(which="minor")
        ax.tick_params(which="minor", size=0)
        plt.show()  
    
    
    def plotKVisibilityMap(self, kvismap, showPlot=True):
        # Get input size
        height, width = kvismap.shape[:2]     
        # Desired "pixelated" size
        w, h = (self.desired_width, self.desired_height)      
        # Resize input to "pixelated" size
        temp = cv2.resize(kvismap, (w, h), interpolation=cv2.INTER_LINEAR)
        nrows, ncols, c = temp.shape # c is channel
        
        self.kvisgridmap = [[0 for x in range(nrows)] for y in range(ncols)]  
        for i in range(nrows):
            for j in range(ncols):
                b,g,r = (temp[i,j])
                self.kvisgridmap[-i][j] = (r,g,b)
        if showPlot == True:
            self.plotGrid(self.kvisgridmap)
        return self.kvisgridmap
    
    def plotTrajectory(self, trajectory_kvalues):
        trajectoryCoordinates = list(trajectory_kvalues[0].keys())
        # print(trajectoryCoordinates)
        for coord in trajectoryCoordinates:
            coordx, coordy = coord[0], coord[1]
            self.gridmap[coordy][coordx] = 0
        routerCoordinates = trajectory_kvalues[1]
        self.gridmap[routerCoordinates[1]][routerCoordinates[0]] = 0
        self.plotGrid(self.gridmap)
    
    def plotWallCoordinates(self, wall_coords):
        
        for coord in wall_coords:
            coordx, coordy = coord[0], coord[1]
            # if self.gridmap[coordy][coordx] == 1:
            #     break # for removing overcrossing lines
            self.gridmap[coordy][coordx] = 1
        self.plotGrid(self.gridmap)
        return self.gridmap
    
    def plotKValueConeshapes(self, kvalue_coneshapes, facecolors, showPlot=True, showGroundTruth=True, resetGrid=False):
        # Reshape gridmap to accept RGB values as array elements
        self.gridmap = np.stack((self.gridmap,)*3, axis=-1)  
        
        kvalues = list(kvalue_coneshapes.keys())
        kvalues.reverse()
        for k in kvalues:
            k_coneshape = kvalue_coneshapes[k]
            if type(k_coneshape) == Polygon:
                facecolor=facecolors[k]
                colorRGB = colors.to_rgb(facecolor)
                for i in range(len(self.gridmap)):
                    for j in range(len(self.gridmap)):
                        if k_coneshape.contains(Point(j,i)):
                            self.gridmap[i][j]=colorRGB
            elif type(k_coneshape) == list:
                for p in k_coneshape:
                    facecolor=facecolors[k]
                    colorRGB = colors.to_rgb(facecolor)
                    for i in range(len(self.gridmap)):
                        for j in range(len(self.gridmap)):
                            if p.contains(Point(j,i)):
                                self.gridmap[i][j]=colorRGB
        if showPlot == True:
            self.plotGrid(self.gridmap)
            
        if showGroundTruth == True:
            self.plotFloorplanGroundTruth(self.ground_truth_image)    
        
        return self.gridmap