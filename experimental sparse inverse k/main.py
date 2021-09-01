import data_processing as dp
import occupancy_grid_map as ogm


# Extract data
data = dp.Data("data/imu2.csv", "data/wifi1.txt")

# Obtain coordinates of trajectory and corresp. kvals
x_stretch, y_stretch = 80, 65
x_translate, y_translate = 50, 51
coords = data.getPositionCoordinates(x_stretch, y_stretch, x_translate, y_translate)
coordsandkvals = data.associateCoordsandKVals() # coordinates scaled to 80x80 gridmap
data.plotIMUTrajectory()


# data2 = dp.Data("data/HIMU-2021-08-31_13-14-02.csv", "data/wifi1.txt")
# data2.plotIMUTrajectory()


# Initialize occupancy grid map
testmap = ogm.GridMap(80,80, coordsandkvals, 3)
testmap.plotTrajectory(coords)

# # Sparse inverse k-vis functionality
kval_lists = testmap.getKValueLists(3, coordsandkvals)
k_val_dictionary = testmap.getKValueDictionary(coordsandkvals)
routerpt = coords[0]
testmap.updateGridMap(coords, routerpt, k_val_dictionary)



