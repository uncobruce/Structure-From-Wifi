import numpy as np
import pandas as pd
import math
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.cluster import KMeans
import datetime
import matplotlib.dates as mdates

class Data:
    ''' Data object used to process data and turn IMU-RSSI data to Coordinates-kvalues'''
    def __init__(self, imufile, wififile):
        self.df = pd.read_csv(imufile, skiprows=4, names = ['ax','ay','az','tx','ty','tz','lat','log','alt']).iloc[:,:]
        print(self.df.head())
        f = open(wififile, "r")
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
        self.rssi = [float(line[1]) for line in array]
        time1 = [datetime.datetime.strptime(line[0],"%H:%M:%S") for line in array]
        self.time = [mdates.date2num(line) for line in time1]
        self.t = np.array(self.time)
        self.db = np.array(self.rssi)
        self.x_stretch, self.y_stretch = 4, 10
        self.x_translate, self.y_translate = 70, 15
        
    def getPositionCoordinates(self, x_stretch, y_stretch, x_translate, y_translate):
        self.x_stretch, self.y_stretch = x_stretch, y_stretch
        self.x_translate, self.y_translate = x_translate, y_translate
        ax = np.array(self.df['ax']) - self.df['ax'].mean()
        ay = np.array(self.df['ay']) - self.df['ay'].mean()
        az = np.array(self.df['az']) - self.df['az'].mean()
        dt = 0.01
        
        vy = []
        v = 0
        for i in range(ay.shape[0]):
            v = v + ay[i]*dt
            vy.append(v)
            
        vy = np.array(vy)
        dy = vy * dt
        
        vx = []
        v = 0
        for i in range(ax.shape[0]):
            v = v + ax[i]*dt
            vx.append(v)
            
        vx = np.array(vx)
        dx = vx * dt
        
        
        rot_angle = 2 * np.arcsin(np.array(self.df['tz']))

        x = 0
        y = 0
        self.X = []
        self.Y = []
        for i in range(ax.shape[0]-1):
            x = x + dx[i+1] * np.sin(rot_angle[i])
            y = y + dy[i+1] * np.cos(rot_angle[i]) 
            self.X.append(-x)
            self.Y.append(-y)
        coordinates = list(zip(self.X, self.Y))
        
        coordinates_scaled = []
        for coord in coordinates:
            x, y = coord[0], coord[1]
            x_scaled, y_scaled = ((x*x_stretch)+x_translate), ((y*y_stretch)+y_translate)
            coordinates_scaled.append((int(x_scaled), int(y_scaled)))
        
        self.coordinates = list(dict.fromkeys(coordinates_scaled))
        
        return self.coordinates

    def getKValues(self, n_clusters=4):
        # TODO automate for diff number of clusters
        Z = np.column_stack((self.t,self.db))
        self.kmeans = KMeans(n_clusters, init ='k-means++', max_iter=300, n_init=10,random_state=0 )
        self.y_kmeans = self.kmeans.fit_predict(Z)
        c0 = self.kmeans.cluster_centers_[:,1][0]
        c1 = self.kmeans.cluster_centers_[:,1][1]
        c2 = self.kmeans.cluster_centers_[:,1][2]
        c3 = self.kmeans.cluster_centers_[:,1][3]
        centroids = [c0, c1, c2, c3]
        centroids.sort(reverse=True)
        C0 = centroids[0]
        C1 = centroids[1]
        C2 = centroids[2]
        C3 = centroids[3]
        # self.t1 = (C0 + C1)/2 
        # self.t2 = (C1 + C2)/2
        # self.t3 = (C2+C3)/2
        # print(self.t1, self.t2, self.t3)
        self.t1 = -35.8
        self.t2 = -45.7
        self.t3 = -56.3    
        
        temp = []
        for db in self.rssi:
            for i in range(20):
                temp.append(db)
        rssi = temp[0:len(self.coordinates)]
        
        self.kvals = []
        for val in rssi:
            if val >= self.t1:
                self.kvals.append(0)
            elif val < self.t1 and val >= self.t2:
                self.kvals.append(1)
            elif val < self.t2 and val >= self.t3:
                self.kvals.append(2)
            elif val < self.t3:
                self.kvals.append(3)
        return self.kvals
        
    
    
    def associateCoordsandKVals(self):
        # coordinates = self.getPositionCoordinates()
        # kvals = self.getKValues()
        self.getPositionCoordinates(self.x_stretch, self.y_stretch, self.x_translate, self.y_translate)
        self.getKValues()
   
        self.coordsandkvals = list(zip(self.coordinates, self.kvals))
        # print(self.coordsandkvals)
        return self.coordsandkvals
    
    
    def plotRSSI(self):
        plt.plot(self.t,self.db,'o')
        plt.gcf().autofmt_xdate()
        plt.xlabel('time')
        plt.ylabel('RSSI (dB)')
        plt.show()


    def plotIMUTrajectory(self):
        self.getPositionCoordinates(self.x_stretch, self.y_stretch, self.x_translate, self.y_translate)
        plt.scatter(self.X,self.Y)
        plt.title("Aprox trajectory without GPS")
        plt.xlabel("X-axis")
        plt.ylabel("Y-axis")
        plt.show()
        
    