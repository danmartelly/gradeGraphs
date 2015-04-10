import json
import numpy as np
from scipy.optimize import curve_fit
import dataFuncs as df

def poly3(x, a, b, c, d):
    return a*x**3 + b*x**2 + c*x + d

def sinusoid(x, r, theta, phase):
    return (r**x)*np.sin(theta*(x-phase))

def absolute(x, slope, xoffset, yoffset):
    return np.absolute(x - xoffset) + yoffset

def getArrayData(studentID, graphIndex):
    cont = df.getGraphData(studentID, graphIndex)
    if cont == None: return None
    try:
        rawData = json.loads(cont)
    except:
        return None
    gdata = rawData['data']
    xdata = []
    ydata = []
    for (x,y) in gdata:
        xdata.append(x)
        ydata.append(y)
    xdata = np.array(xdata)
    ydata = np.array(ydata)
    return xdata, ydata

def interpolate(x1,y1,x2,y2,x):
    return y1 + (y2-y1)*(x-x1)/(x2-x1)

def generatePoints(f, xstart, xend, step):
    ans = []
    while (xstart < xend):
        ans.append([xstart, f(xstart)])
        xstart += step
    return ans

def addLinearInterpolation(xdata, ydata, step):
    i = 0
    xdata = list(xdata)
    ydata = list(ydata)
    while (i < len(xdata)-1):
        diff = xdata[i+1] - xdata[i]
        if (diff > step):
            (x1,y1,x2,y2) = (xdata[i], ydata[i], xdata[i+1], ydata[i+1])
            x = xdata[i] + step
            xdata.insert(i+1, x)
            ydata.insert(i+1, interpolate(x1,y1,x2,y2,x))
        i += 1
    return np.array(xdata), np.array(ydata)

def fitData(f, xdata, ydata):
    xdata, ydata = addLinearInterpolation(xdata, ydata, .1)
    try:
        popt, pcov = curve_fit(f, xdata, ydata)
    except:
        return [], -1
    args = [xdata] + list(popt)
    residuals = ydata - f(*args)
    fres = sum(residuals**2)
    return (popt, fres)

def tryFitsOnData(xdata, ydata):
    fs = [poly3, sinusoid, absolute]
    ans = []
    for f in fs:
        ans.append(fitData(f, xdata, ydata))
    return ans

def tryFits(studentID, graphIndex):
    xdata, ydata = getArrayData(studentID, graphIndex) 
    return tryFitsOnData(xdata, ydata)


