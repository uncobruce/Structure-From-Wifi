''' Create an object containing the trajectory end points, associating
    k-values, and the router point for the desired grid size.'''
import csv
class trajectoryObject:
    
    def __init__(self, trajectory_endpts_path, kvisplot_path):
        self.trajectoryEndPointsPath = trajectory_endpts_path
        self.kVisibilityPlotPath = kvisplot_path
        
    def obtainTrajectoryCoordinates(self):
        trajEndPoints=[]
        with open(self.trajectoryEndPointsPath, "r") as trajectoryEndPointsFile:
            data = list(tuple(line) for line in csv.reader(trajectoryEndPointsFile))
        print(data)