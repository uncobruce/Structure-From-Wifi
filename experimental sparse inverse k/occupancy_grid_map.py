import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon
import numpy as np
import cv2
import math
from bresenham import bresenham
from shapely.ops import polygonize

class GridMap:
    def __init__(self, desired_width, desired_height, coordsandkvals, max_kval_visible_distance):
        self.desired_width = desired_width
        self.desired_height = desired_height
        self.gridmap = np.zeros(desired_width*desired_height)
        self.gridmap = self.gridmap.reshape(((desired_width, desired_height)))
        self.gridmap[self.gridmap == 0] = 0.5
        self.max_kval_visible_distance = max_kval_visible_distance
    def plotGrid(self):  
        fig, ax = plt.subplots()
        ax.imshow(self.gridmap, cmap="Greys", origin="lower", vmax=1)
        ax.set_xticks(np.arange(self.desired_height+1)-0.5, minor=True)
        ax.set_yticks(np.arange(self.desired_width+1)-0.5, minor=True)
        ax.grid(which="minor")
        ax.tick_params(which="minor", size=0)    
        plt.show()
        
    def plotTrajectory(self, coordinates):
        trajlines=[]
        for i in range(len(coordinates)-1):
            pt1 = coordinates[i]
            pt2 = coordinates[i+1]
            line = list(bresenham(int(pt1[0]), int(pt1[1]), int(pt2[0]), int(pt2[1])))
            trajlines.append(line)
        for line in trajlines:
            for pt in line:
                self.gridmap[pt[1]][pt[0]] = 0
        self.plotGrid()

    def getKValueCoordinates(self, desiredKValue, coordsandkvals):
        kValCoordinates = []
        for i in range(len(coordsandkvals)-1):
            position = coordsandkvals[i][0]
            kval = coordsandkvals[i][1]
            if kval == desiredKValue and position not in kValCoordinates:
                kValCoordinates.append(position)
        kValCoordinates.sort()
        return kValCoordinates
    
    def getKValueLists(self, maxKValue, coordsandkvals):
        self.kvaluelists=[]
        for i in range(maxKValue+1):
            kval_list = self.getKValueCoordinates(i, coordsandkvals)
            self.kvaluelists.append(kval_list)
        return self.kvaluelists
    
    def getKValueDictionary(self, coordsandkvals):  
        self.k_val_dictionary = {}
        for i in range(len(self.gridmap)):
            for j in range(len(self.gridmap[0])):
                coordinate = (j,i)
                self.k_val_dictionary[coordinate] = None
        for i in range(len(coordsandkvals)-1):
            position = coordsandkvals[i][0]
            kval = coordsandkvals[i][1]
            self.k_val_dictionary[position] = kval
        return self.k_val_dictionary
    
    def checkNeighbouringCells(self, k, currentkval, trajectoryCoordinates):
        for i in range(len(self.gridmap)-1): # i is grid row
            for j in range(len(self.gridmap[0])-1): # j is grid col in that row
                y, x = i, j
                point1 = np.array((x,y))
                point2 = np.array(k)
                distanceToKValue = int(np.linalg.norm(point2-point1))
                if distanceToKValue == 0: continue
                elif distanceToKValue > self.max_kval_visible_distance: continue
                else:
                    current_cell_value = self.gridmap[y][x]
                    current_cell_kvalue = self.k_val_dictionary[(x,y)]
                    same_kval_factor = 1 / distanceToKValue 
                    current_cell_value = self.gridmap[y][x]
                    P_same_kval = current_cell_value * (1 - same_kval_factor)
                    P_occ = (1 - (current_cell_value * (1 - same_kval_factor)))
                    if current_cell_kvalue == None:
                        self.gridmap[y][x] = P_same_kval 
                        self.k_val_dictionary[(x,y)] = currentkval
                    elif current_cell_kvalue == currentkval-1  :
                           self.gridmap[y][x] = P_occ + .2
                           self.k_val_dictionary[(x,y)] = currentkval
                           return 
       


    def updateGridMap(self,  trajectoryCoordinates, routerpt, k_val_dictionary):
        self.k_val_dictionary = k_val_dictionary
        for i in range(len(self.kvaluelists)):
            kvals = self.kvaluelists[i]
            currentkval = i
            for k in kvals:
                self.checkNeighbouringCells(k, currentkval, trajectoryCoordinates)
                
        self.plotGrid()
            


