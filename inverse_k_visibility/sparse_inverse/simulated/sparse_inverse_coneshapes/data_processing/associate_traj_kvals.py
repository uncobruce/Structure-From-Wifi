''' Create an object containing the trajectory end points, associating
    k-values, and the router point for the desired grid size.'''
import csv
from bresenham import bresenham

class trajectoryObject:
    
    def __init__(self, trajectory_endpts_path, kvisplot_path):
        self.trajectoryEndPointsPath = trajectory_endpts_path
        self.kVisibilityPlotPath = kvisplot_path
        
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
        
