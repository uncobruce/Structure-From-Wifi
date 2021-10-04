import math
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import numpy as np
import pandas as pd
f = open("rssi data.txt", "r")

rssiData = []

for line in f:
    row = line.split()
    row_new = []
    
    for i in range(len(row)-1):
        if i == 1 or i == (len(row))-2:
            newData = row[i]
            if i == len(row)-2:
                newData = float(row[i])
            
            row_new.append(newData)
    
    rssiData.append(row_new)    
f.close()
array = np.asarray(rssiData)

time = [datetime.datetime.strptime(line[0],"%H:%M:%S") for line in array]
time1 = [mdates.date2num(line) for line in time]

rssi = [float(line[1]) for line in array]

x = np.array(time)
y = np.array(rssi)

x1 = np.array(time1)

plt.plot(x,y,'o')
plt.gcf().autofmt_xdate()
plt.xlabel('time')
plt.ylabel('RSSI (dB)')
plt.show()

from sklearn.cluster import KMeans

X = np.column_stack((x1,y))


kmeans = KMeans(n_clusters=4, init ='k-means++', max_iter=300, n_init=10,random_state=0 )
y_kmeans = kmeans.fit_predict(X)
plt.scatter(X[y_kmeans==0, 0], X[y_kmeans==0, 1], s=100, c='red', label ='Cluster 1')
plt.scatter(X[y_kmeans==1, 0], X[y_kmeans==1, 1], s=100, c='blue', label ='Cluster 2')
plt.scatter(X[y_kmeans==2, 0], X[y_kmeans==2, 1], s=100, c='green', label ='Cluster 3')
plt.scatter(X[y_kmeans==3, 0], X[y_kmeans==3, 1], s=100, c='purple', label ='Cluster 4')

plt.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1], s=300, c='yellow', label = 'Centroids')


c0 = kmeans.cluster_centers_[:,1][0]
c1 = kmeans.cluster_centers_[:,1][1]
c2 = kmeans.cluster_centers_[:,1][2]
c3 = kmeans.cluster_centers_[:,1][3]

print('centroids (dB):',c0, c1, c2, c3)

#rssi thresholds
t1 = (c0 + c1)/2 
t2 = (c1 + c2)/2
t3 = (c2+c3)/2
print('t1:',t1, 't2:',t2, 't3:', t3)

print('\n0 walls: RSSI >',t1, 'dB')
print('1 wall: RSSI between',t1,'&',t2, 'dB')
print('2 walls: RSSI between',t2,'&',t3, 'dB')
print('3 walls: RSSI less than', t3, 'dB')

wallLabels = []

for rssiValue in y:
    if rssiValue > t1:
        wallLabels.append(0)
    elif rssiValue < t1 and rssiValue > t2:
        wallLabels.append(1)
    elif rssiValue < t2 and rssiValue > t3:
        wallLabels.append(2)
    elif rssiValue < t3:
        wallLabels.append(3)

# wallLabelsNP = np.array(wallLabels)
# array2 = np.column_stack((wallLabelsNP,y))
# array2 = array2[np.argsort(array2[:,0])] #sort rssi values by label
