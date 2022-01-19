# -*- coding: utf-8 -*-
"""
Created on Tue Jan 11 17:25:46 2022

@author: jzala
"""

def squareTrajectory(trajectory_kvalues):
    trajectory = list(trajectory_kvalues[0].keys())
    new_trajectory_kval_map = {}
    for i in range(len(trajectory)-1):
        point1 = trajectory[i]
        point2 = trajectory[i+1]
        intermediate_pt = (point2[0], point1[1])
        intermediate_kvalue = trajectory_kvalues[0][point1]
        new_trajectory_kval_map[intermediate_pt] = intermediate_kvalue
        
    new_trajectory_kvalues = (new_trajectory_kval_map, trajectory_kvalues[1])
    print(new_trajectory_kvalues == trajectory_kvalues)
    return new_trajectory_kvalues
    
        
    