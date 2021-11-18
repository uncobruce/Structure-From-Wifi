''' Create an object containing the trajectory end points, associating
    k-values, and the router point for the desired grid size.'''
from bresenham import bresenham

class trajectoryObject:
    
    def __init__(self, trajectory_endpts_path, kvisplot_path, grid_width, grid_height, router_coords_unscaled, axis_limits):
        self.trajectoryEndPointsPath = trajectory_endpts_path
        self.kVisibilityPlotPath = kvisplot_path
        self.routerX = int(((int(grid_height))*router_coords_unscaled[0])/axis_limits[0])
        self.routerY = int(((int(grid_width))*router_coords_unscaled[1])/axis_limits[1])
        self.routerCoords = (self.routerX, self.routerY)
        
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
        return self.trajectoryCoordinates
        
    def obtainTrajectoryKValues(self):
        pass