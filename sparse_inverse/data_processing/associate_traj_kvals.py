''' Create an object containing the trajectory end points, associating
    k-values, and the router point for the desired grid size.'''
from bresenham import bresenham
from matplotlib import colors as colors

class trajectoryObject:
    
    def __init__(self, trajectory_endpts_path, kvisplot_path, grid_width, grid_height, router_coords_unscaled, axis_limits, kvaluescolordict, kvis_gridmap):
        self.trajectoryEndPointsPath = trajectory_endpts_path
        self.kVisibilityPlotPath = kvisplot_path
        self.routerX = int(((int(grid_height))*router_coords_unscaled[0])/axis_limits[0]) + 5
        self.routerY = int(((int(grid_width))*router_coords_unscaled[1])/axis_limits[1]) - 1 #TODO automate
        self.routerCoords = (self.routerX, self.routerY)
        self.kvaluescolordict = kvaluescolordict
        self.kvis_gridmap = kvis_gridmap
        
    def obtainTrajectoryCoordinates(self):
        trajEndPoints=[]
        # parse text file and obtain end points
        with open(self.trajectoryEndPointsPath, "r") as trajectoryEndPointsFile:
            for line in trajectoryEndPointsFile:
                end_point = (int(line[0:2]), int(line[3:-2])) 
                trajEndPoints.append(end_point)
                
        # convert endpoints to list of lines
        linestoplot=[]
        for i in range(len(trajEndPoints)-1):
            p1 = trajEndPoints[i]
            p2 = trajEndPoints[i+1]
            line = list(bresenham(p1[0],p1[1], p2[0],p2[1]))
            linestoplot.append(line)
            
        self.trajectoryCoordinates=[] # add list  of lines to trajectory coordinates list
        for line in linestoplot:
            for point in line:
                self.trajectoryCoordinates.append(point)
        
        self.trajectoryCoordinates = list(dict.fromkeys(self.trajectoryCoordinates))
        # print(self.trajectoryCoordinates)
        return self.trajectoryCoordinates
    
    
        
    def obtainTrajectoryKValues(self):
        # def nearestcolor(color, colorslist): 
        #     r, g, b = color[0], color[1], color[2]
            
        #     smallest_distance, closest_color = 0, None
        #     for other_color in colorslist:
        #         r2, g2, b2 = int(other_color[0]), int(other_color[1]),int( other_color[2]) #conv to int to avoid runtime warning
        #         distance = abs(r2 - r) + abs(g2 - g) + abs(b2 - b)
        #         if distance < smallest_distance or closest_color == None:
        #             smallest_distance = distance
        #             closest_color = other_color
        #     return closest_color
            
        self.trajectory_kvalues_dict = {}
      
        for point in self.trajectoryCoordinates:
            correspKValColor = self.kvis_gridmap[point[1]][point[0]]  
            
            if correspKValColor in self.kvaluescolordict.keys():
                correspKValue = self.kvaluescolordict[correspKValColor]
                self.trajectory_kvalues_dict[point] = correspKValue
         
            else: # if point colour not found, take the colour of a point behind it
                point_index = self.trajectoryCoordinates.index(point)
                prev_point = self.trajectoryCoordinates[point_index - 3]
                
                correspKValColor = self.kvis_gridmap[prev_point[1]][prev_point[0]]  
                correspKValue = self.kvaluescolordict[correspKValColor]
          
                self.trajectory_kvalues_dict[point] = correspKValue 
    
    def getTrajectoryKValuesObject(self):
        self.obtainTrajectoryCoordinates()
        self.obtainTrajectoryKValues()
        return self.trajectory_kvalues_dict, self.routerCoords
    
