import numpy as  np
import math

LON_MIN_INDEX = 0
LON_MAX_INDEX = 1
LAT_MIN_INDEX = 2
LAT_MAX_INDEX = 3
FLAT_INDEX_INDEX = 4

def generate_grid(xMin,xMax,yMin,yMax,step,precision):
    noOfXSteps = math.floor(np.around(((xMax-xMin)/step),0))
    noOfYSteps = math.floor(np.around(((yMax-yMin)/step),0))

    yGrid = np.linspace(yMin,yMax,num = (noOfYSteps-1))
    
    xGrid = []
    for i in range(noOfXSteps):
        xGrid.append(xMin + (i*step))
    xGrid = np.array(xGrid)
    xGrid = np.around(xGrid,precision)
    
    yGrid = []
    for i in range(noOfYSteps):
        yGrid.append(yMin + (i*step))
    yGrid = np.array(yGrid)
    yGrid = np.around(yGrid,precision)
    
    xYMinMax = []
    gridCounter = 0
    for i in range(0,yGrid.shape[0]):
        for j in range(0,xGrid.shape[0]):
            if(i < (yGrid.shape[0]-1)):
                if(j < (xGrid.shape[0]-1)):
                    localXMin = xGrid[j]
                    localXMax = xGrid[j+1]
                    localYMin = yGrid[i]
                    localYMax = yGrid[i+1]
                else:
                    localXMin = xGrid[j]
                    localXMax = np.around(xGrid[j]+step,precision)
                    localYMin = yGrid[i]
                    localYMax = yGrid[i+1]
            else:
                if(j < (xGrid.shape[0]-1)):
                    localXMin = xGrid[j]
                    localXMax = xGrid[j+1]
                    localYMin = yGrid[i]
                    localYMax = np.around(yGrid[i]+step,precision)
                else:
                    localXMin = xGrid[j]
                    localXMax = np.around(xGrid[j]+step,precision)
                    localYMin = yGrid[i]
                    localYMax = np.around(yGrid[i]+step,precision)        
            xYMinMax.append([localXMin,localXMax,localYMin,localYMax,gridCounter])
            gridCounter = gridCounter + 1
    return xGrid, yGrid, xYMinMax

def compute_mid_point(xMin,xMax,yMin,yMax):
    return (xMax+xMin)/2,(yMax+yMin)/2

#return numpy array
#which can be used for KDE computation
def compute_xy_for_kde(xMin,xMax,yMin,yMax,step,precision):
    _,_,boundary = generate_grid(xMin,xMax,yMin,yMax,step,precision)
    #make array of zeros for return value of xy
    xy = np.zeros((len(boundary),2))
    print(xy.shape)
    for i in range(len(boundary)):
        xy[i,0],xy[i,1] = compute_mid_point(boundary[i][LON_MIN_INDEX],boundary[i][LON_MAX_INDEX],\
                                boundary[i][LAT_MIN_INDEX],boundary[i][LAT_MAX_INDEX])
    return xy

def get_row_col(flatIndex, numRows, numCols):
    if(flatIndex >= (numRows*numCols)):
        return -1,-1
    else:
        row = flatIndex // numCols
        col = flatIndex % numCols
        print(row,col)
        return row,col