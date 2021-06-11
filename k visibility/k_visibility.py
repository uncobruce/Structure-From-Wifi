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

def isLeftTurn(vi, viPrev, viNext):
    # given a vertex, determine if CW or CCW
    # returns True if CCW (left turn), returns False if CW (right turn)
    # print(vi, viPrev, viNext)
    return (  (vi[0] - viPrev[0])*(viNext[1]-vi[1]) - (vi[1]-viPrev[1])*(viNext[0]-vi[0]) > 0  )

def onPositiveSide(vi, viPrev):
    transmitterX = vertices.transmitterCoordsX
    transmitterY = vertices.transmitterCoordsY
    # given a vertex, determine if vPrev is on positive side of the ray 
    # ray is defined as line connected transmitter coords to vi coords
    line = {'x1': transmitterX,'y1':transmitterY,'x2':vi[0],'y2':vi[1]}
    p1 = {'x':viPrev[0],'y':viPrev[1]}
    return (( (line['y1'] - line['y2'])*(p1['x'] - line['x1'])+(line['x2']- line['x1'])*(p1['y']-line['y1']) )>0)

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
# Record all edges and rays in polygon
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
    edgeSegment = {vi, viNext}
    edgeSegments.append(edgeSegment)
    if vertex in criticalVertices2:
       # print("\n",vertex) #ummmm
       criticalRay = {transmitterCoords, vi}
       criticalRays.append(criticalRay)



# Display polygon
# ---------------------------------------------------------------------
cv2.imshow('polygon', img)
cv2.waitKey()
cv2.destroyAllWindows()
    

    