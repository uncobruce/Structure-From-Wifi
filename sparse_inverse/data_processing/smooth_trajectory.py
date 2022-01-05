'''Given an erratic trajectory, return a trajectory with straight lines'''

def smoothTrajectory(trajectory_endpts):
    print(trajectory_endpts)
    new_trajectory_endpts = []
    for i in range(len(trajectory_endpts)-1):
        point1 = trajectory_endpts[i]
        point2 = trajectory_endpts[i+1]
        intermediate_point = (point1[0], point2[1])
        new_trajectory_endpts.append(point1)
        new_trajectory_endpts.append(intermediate_point)
    return new_trajectory_endpts