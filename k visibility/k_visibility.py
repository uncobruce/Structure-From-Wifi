import vertices # import vertices.py, ensure in same directory
import math
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import numpy as np
import pandas as pd
import cv2
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

img = vertices.img
transmitterCoords = (vertices.transmitterCoordsX, vertices.transmitterCoordsY)
transmitterX = vertices.transmitterCoordsX
transmitterY = vertices.transmitterCoordsY
# Given a list of coordinates of a given polygon shape
verticesArray = ([462., 636.], [434., 416.], [599., 382.],[424., 277.],   
                    [709., 197.], [702., 384.], [850., 496.], [877.,  23.],
                    [454.,  14.], [189.,  85.], [ 85., 257.],
                    [100., 474.], [227., 443.], [217., 264.], [351., 264.], [324., 529.],
                    [211., 621.])
verticesArray = np.array(verticesArray, dtype='f')

def isVertexCritical(vi, viPrev, viNext):
    # a vertex is critical if viPrev and viNext are on the same side of 
    # the line given by the points (transmitterCoords, vi)
    # returns True if critical vertex, False otherwise
    transmitterX = vertices.transmitterCoordsX
    transmitterY = vertices.transmitterCoordsY
    transmitterCoords = (transmitterX, transmitterY)
    line = {'x1': transmitterX,'y1':transmitterY,'x2':vi[0],'y2':vi[1]}
    p1 = {'x':viPrev[0],'y':viPrev[1]}
    p2 = {'x':viNext[0],'y':viNext[1]} 
    return ((line['y1'] - line['y2'])*(p1['x'] - line['x1'])+(line['x2']- line['x1'])*(p1['y']-line['y1']))*((line['y1']-line['y2'])*(p2['x']-line['x1'])+(line['x2']-line['x1'])*(p2['y']-line['y1']))>0

def bothPointsOnSameSide(vi, p1, p2):
    transmitterX = vertices.transmitterCoordsX
    transmitterY = vertices.transmitterCoordsY
    transmitterCoords = (transmitterX, transmitterY)
    # print(p1, p2)
    line = {'x1': transmitterX,'y1':transmitterY,'x2':vi[0],'y2':vi[1]}
    p1 = {'x':p1[0],'y':p1[1]}
    p2 = {'x':p2[0],'y':p2[1]} 
    return ((line['y1'] - line['y2'])*(p1['x'] - line['x1'])+(line['x2']- line['x1'])*(p1['y']-line['y1']))*((line['y1']-line['y2'])*(p2['x']-line['x1'])+(line['x2']-line['x1'])*(p2['y']-line['y1']))>0

def isLeftTurn(vi, viPrev, viNext):
    # given a vertex, determine if CW or CCW
    # returns True if CCW (left turn), returns False if CW (right turn)
    # print(vi, viPrev, viNext)
    return (  (vi[0] - viPrev[0])*(viNext[1]-vi[1]) - (vi[1]-viPrev[1])*(viNext[0]-vi[0]) > 0  )

def onPositiveSide(vi, viPrev):
    transmitterX = vertices.transmitterCoordsX
    transmitterY = vertices.transmitterCoordsY
    # given a vertex, determine if vPrev is on positive side of the ray 
    # ray is defined as line connecting transmitter coords to vi coords
    line = {'x1': transmitterX,'y1':transmitterY,'x2':vi[0],'y2':vi[1]}
    p1 = {'x':viPrev[0],'y':viPrev[1]}
    return (( (line['y1'] - line['y2'])*(p1['x'] - line['x1'])+(line['x2']- line['x1'])*(p1['y']-line['y1']) )>0)

# def rayIntersectsEdge(slope, b, edgeSegment):
#     # If a critical ray intersects an edge segment, return the coords of intersection
#     # otherwise return False
#     edgeX1 = min(edgeSegment[0][0], edgeSegment[1][0])
#     edgeX2 = max(edgeSegment[0][0], edgeSegment[1][0])
#     edgeY1 = min(edgeSegment[0][1], edgeSegment[1][1])
#     edgeY2 = max(edgeSegment[0][1], edgeSegment[1][1])
#     transmitterX, transmitterY = vertices.transmitterCoordsX, vertices.transmitterCoordsY
#     # if not (edgeX1 < transmitterX):
#     y1, y2 = (slope)*edgeX1 + b, (slope)*edgeX2 + b       
#     if (y1 > edgeY1 and y2 < edgeY2):
#         slopeEdge = (edgeY2 - edgeY1)/(edgeX2 - edgeX1)
#         bEdge = edgeY1 - slopeEdge*edgeX1
#         b2, b1 = max(bEdge, b), min(bEdge, b)
#         slope2, slope1 = max(slopeEdge, slope), min(slopeEdge, slope)
#         print(slope, b, slopeEdge, bEdge)
#         xInt = (b2 - b1) / (slope2 - slope1)
#         yInt = (slopeEdge*xInt) + bEdge
#         if (xInt < edgeX1 or xInt > edgeX2):
#             return False
#         q = (xInt, yInt)
#         v_j_prev = (edgeX1, edgeY1)
#         return (q, v_j_prev)
#     return False
# Step 1: Get critical vertices
# ---------------------------------------------------------------------
i=0
criticalVertices = []    
for vertex in verticesArray:
    if i == 0:
        i+=1
        continue
    viX, viY = vertex.ravel()
    vi = (viX, viY)
    
    viPrevX, viPrevY = verticesArray[i-1].ravel()
    viPrev = (viPrevX, viPrevY)
    
    if i < len(verticesArray) - 1:
        viNextX, viNextY = verticesArray[i+1].ravel()
        i+=1
    else:
        viNextX, viNextY = verticesArray[0].ravel()  
    viNext = (viNextX, viNextY)

    isCriticalVertex = isVertexCritical(vi, viPrev, viNext)
    if isCriticalVertex:
        criticalVertices.append(vi)
criticalVertices2 = np.array(criticalVertices)

# Colour all critical vertices in pink 
for criticalVertex in criticalVertices2:
    # print(criticalVertex)
    crX, crY = criticalVertex.ravel()
    cv2.circle(img, (crX, crY), 6, (127, 0, 255), -1)

# Step 2a: Apply +1/-1 rule to each critical vertex
# ---------------------------------------------------------------------
i=0
plus1Points=[]
minus1Points=[]    
for vertex in verticesArray:
    if i == 0:
        i+=1
        continue
    viX, viY = vertex.ravel()
    vi = (viX, viY)
    
    viPrevX, viPrevY = verticesArray[i-1].ravel()
    viPrev = (viPrevX, viPrevY)
    
    if i < len(verticesArray) - 1:
        viNextX, viNextY = verticesArray[i+1].ravel()
    else:
        viNextX, viNextY = verticesArray[0].ravel()  
    viNext = (viNextX, viNextY)
    i+=1

    if vertex in criticalVertices2:
       # print("\n",vertex) #ummmm
        if isLeftTurn(vi, viPrev, viNext):
            if onPositiveSide(vi, viPrev):
                plus1Points.append(vertex)
            else:
                minus1Points.append(vertex)
        else: # right turn
            if onPositiveSide(vi, viPrev):
                minus1Points.append(vertex)
            else:
                plus1Points.append(vertex)

# Step 2b: Apply +2/-2 rule
# ---------------------------------------------------------------------
# Record all edges and critical rays in polygon
edgeSegments=[]
criticalRays=[]
i=0
for vertex in verticesArray:
    viX, viY = vertex.ravel()
    vi = (viX, viY)
    if i < len(verticesArray) - 1:
        viNextX, viNextY = verticesArray[i+1].ravel()
    else:
        viNextX, viNextY = verticesArray[0].ravel() 
    viNext = (viNextX, viNextY)
    i+=1
    edgeSegment = [vi, viNext]
    edgeSegments.append(edgeSegment)
    if vertex in criticalVertices2:
       # print("\n",vertex) # ummmm
       criticalRay = [transmitterCoords, vi]
       criticalRays.append(criticalRay)

# Identify where critical rays intersect edge segments and apply rule
plus2Points=[]
minus2Points=[]
qPoints=[]

def rayIntersectsEdge(slopeRay, bRay, edge1, edge2):
    # If a critical ray intersects an edge segment, return True
    # otherwise return False
    edgeX1 = min(edgeSegment[0][0], edgeSegment[1][0])
    edgeX2 = max(edgeSegment[0][0], edgeSegment[1][0])
    edgeY1 = min(edgeSegment[0][1], edgeSegment[1][1])
    edgeY2 = max(edgeSegment[0][1], edgeSegment[1][1])
    transmitterX, transmitterY = vertices.transmitterCoordsX, vertices.transmitterCoordsY
    y1, y2 = (slopeRay*edgeX1)+bRay, (slopeRay*edgeX2)+bRay
    if (y1 > edgeY1 and y2 < edgeY2):
        return True  
    return False

    
for edgeSegment in edgeSegments:
    p1, p2 = edgeSegment[0], edgeSegment[1]
    slopeEdge = (p2[1] - p1[1]) / (p2[0] - p1[0])
    bEdge = p1[1] - (slopeEdge)*(p1[0])
    transmitterX = vertices.transmitterCoordsX
    transmitterY = vertices.transmitterCoordsY
    for ray in criticalRays:
        xRay, yRay = ray[1][0], ray[1][1]
        raycoords = (xRay, yRay)
        slopeRay = (yRay - transmitterY) / (xRay - transmitterX)
        bRay = yRay - (slopeRay*xRay)
        checkIntersection = rayIntersectsEdge(slopeRay, bRay, p1, p2)
        if checkIntersection is True:
            slope1, slope2 = min(slopeRay, slopeEdge), max(slopeRay, slopeEdge)
            b1, b2 = min(bRay, bEdge), max(bRay, bEdge)
            xInt = round((b2 - b1) / (slope2 - slope1), 1)
            yInt = round((slopeEdge*xInt) + bEdge, 1)
            q = (xInt, yInt)
            # vjPrevX = min(edgeSegment[0][0], edgeSegment[1][0])
            # vjPrevY = min(edgeSegment[0][1], edgeSegment[1][1])
            vjPrev = p1
            if not (q == p1 or q == p2): 
                if not (((yRay and yInt>0) and yInt > yRay) or (yRay and yInt < 0) and (yInt < yRay)):
                    qPoints.append(q) # graph is flipped so need to do a "not" operation for the right answer
                    i=0
                    for vertex in verticesArray:
                        viX, viY = vertex.ravel()
                        vi = (viX, viY)
                        if vi == raycoords:
                            if i > 0 and i < len(verticesArray):
                                viPrevX, viPrevY = verticesArray[i-1].ravel()
                                viPrev = (viPrevX, viPrevY)
                            if bothPointsOnSameSide(vi, viPrev, vjPrev):
                                minus2Points.append(q)
                            else:
                                plus2Points.append(q)
                        i+=1
for q in qPoints:
    for vertex in criticalVertices2:
        vX, vY = vertex.ravel()
        vi = (vX, vY)
        if q == vi:
            qPoints.remove(q)
            continue
    qX, qY = int(q[0]), int(q[1])
    if q in minus2Points:
        cv2.circle(img, (qX, qY), 6, (175, 165, 50), -1)
    elif q in plus2Points:
        cv2.circle(img, (qX, qY), 6, (100, 200, 250), -1)

# for vertex in verticesArray:
#     x,y = vertex.ravel()
#     plt.scatter(x, y)
    
plt.show()
    

# Display polygon
# ---------------------------------------------------------------------
cv2.imshow('polygon', img)
cv2.waitKey()
cv2.destroyAllWindows()
