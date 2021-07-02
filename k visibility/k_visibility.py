import matplotlib.pyplot as plt
from shapely.geometry import  Point, Polygon, LineString, GeometryCollection
import numpy as np
import cv2
import math
from bresenham import bresenham

def isVertexCritical(criticalRay, p1, p2):
    # criticalRay: LineString object giving critical ray
    # return True if vertex is critical vertex 
    router = criticalRay.coords[0]
    vi = criticalRay.coords[1]
    routerx, routery = router[0], router[1]
    line = {'x1': routerx,'y1':-routery,'x2':vi[0],'y2':-vi[1]}
    p1 = {'x':p1[0],'y':-p1[1]}
    p2 = {'x':p2[0],'y':-p2[1]} 
    return ((line['y1'] - line['y2'])*(p1['x'] - line['x1'])+(line['x2']- line['x1'])*(p1['y']-line['y1']))*((line['y1']-line['y2'])*(p2['x']-line['x1'])+(line['x2']-line['x1'])*(p2['y']-line['y1']))>0

# Create list of points from given vertices
verticesArray = ([462., 636.], [434., 416.], [599., 382.],[424., 277.],   
                    [709., 197.], [702., 384.], [850., 496.], [877.,  23.],
                    [454.,  14.], [189.,  85.], [ 85., 257.],
                    [100., 474.], [227., 443.], [217., 264.], [351., 264.], [324., 529.],
                    [211., 621.])
points = []
for v in verticesArray:
    px, py = v[0], -v[1]
    p = (px,py)
    points.append(p)

# Define router position
routerx, routery = 400, -570

# Create polygon from vertices and plot
poly = Polygon(points)
coordinates = list(poly.exterior.coords)
plt.plot(*poly.exterior.xy)

for point in coordinates:
    px, py = point[0], point[1]
    plt.plot(px, py, 'bo')    
    
# STEP 1) Find and plot critical vertices
# -------------------------------------------------------------------------
routerPoint = Point((routerx, routery))
i=0
criticalvertices=[]
for coord in coordinates:
    coord2 = (coord[0] + 100, coord[1]+100)
    rc = LineString([routerPoint, coord])
    if i!=0 and i!= len(coordinates)-1:
        if isVertexCritical(rc, coordinates[i-1], coordinates[i+1]):
            criticalvertices.append(coord)
            plt.plot(*rc.xy, 'k--',linewidth=2.0,)
            plt.plot(coord[0],coord[1],'ro')
            
    i+=1
plt.plot(routerx, routery, 'go') # plot router point   
#plt.show()

# STEP 2) Checking ray-poly intersections
# -------------------------------------------------------------------------
def extendRay(routerPoint, vertex):
    x1, y1 = routerPoint.x, routerPoint.y
    x2, y2 = vertex[0], vertex[1]
    extendLength = 1000
    diff = (x2-x1, y2-y1)
    mag = math.sqrt((x2-x1)**2 + (y2-y1)**2)
    norm = (diff[0] / mag, diff[1]/mag) 
    p3 = (vertex[0] + extendLength*norm[0],vertex[1] + extendLength*norm[1])
    x3,y3 = p3[0], p3[1]
    return (x3,y3)

for v in criticalvertices:
    rc = LineString([routerPoint, v])
    v2 = extendRay(routerPoint, v)
    rc2 = LineString([v, v2])
    a = poly.exterior.intersection(rc2)
    plt.plot(*rc2.xy, 'k--',linewidth=2.0,)
    if a.geom_type == 'MultiPoint':
        for i in range(len(a)):
            b = tuple(a.bounds)
            ax, ay = a[i].x, a[i].y
            coord = (ax, ay)
            if coord not in coordinates:
                plt.plot(ax, ay, 'ko')
    elif a.geom_type == 'Point':
        b = tuple(a.coords[0])
        if b not in coordinates:
            plt.plot(*a.coords.xy[0], *a.coords.xy[1], 'ko')

    

# Show final result
plt.xlim(50, 900)
plt.ylim(-700, 0)
plt.show()
