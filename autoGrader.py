import numpy as np
import fitBackend
import dataFuncs
import os
import cgi
import cgitb
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
cgitb.enable() 

resUpperThresh = 900. # if above thresh, give 0%
resLowerThresh = 100. # if below thresh, give 100%
paramThresh1 = .1 # if param within thresh, give 100%
paramThresh2 = .2 # if param outside thresh, give 0%

# answerType: 0 -> cubic, 1 -> sinusoid, 2 -> absolute
# answerParams: answer coefficients of function
def curveGrader(xdata, ydata, (answerType, answerParams)):
    fits = fitBackend.tryFitsOnData(xdata, ydata)
    bestIndex = -1
    for i in range(3):
        (popt, fres) = fits[i]
        if (fres >= 0) and (bestIndex == -1 or fres < fits[bestIndex][1]):
            bestIndex = i
    if (bestIndex != answerType):
        return 0, ['wrong classification']
    (popt, fres) = fits[bestIndex]
    grade = 100
    reasons = []
    # assign grade based on residual
    resGrade = 1. - (fres - resLowerThresh)/(resUpperThresh - resLowerThresh)
    resGrade *= 100
    resGrade = max(min(100, resGrade), 0)
    if (resGrade < 100): reasons.append('res')
    grade = min(grade, resGrade)
    # assign grade based on function parameters
    for i in range(len(popt)):
        if abs(answerParams[i]) < .5:
            paramGrade = 100 if popt[i] < .5 else 0
        else:
            ratioDistance = abs(popt[i] - answerParams[i])/answerParams[i]
            paramGrade = 1. - (ratioDistance - paramThresh1)/(paramThresh2 - paramThresh1)
        paramGrade *= 100
        paramGrade = max(min(100, paramGrade), 0)
        if (paramGrade < 100): reasons.append('param'+str(i))
        grade = min(grade, paramGrade)
    return grade, reasons

def floatRange(start, stop, step):
    while (start < stop):
        yield start
        start += step

# returns [(x0,y0),(x1,y1)...]
def getLocalExtrema(mathFunc, loLimit, hiLimit, step = None):
    answer = []
    if step == None: step = (hiLimit-loLimit)/100.
    for x in floatRange(loLimit, hiLimit, step):
        if (mathFunc(x) > mathFunc(x+step) and mathFunc(x) > mathFunc(x-step))\
          or (mathFunc(x) < mathFunc(x+step) and mathFunc(x) < mathFunc(x-step)):
            answer.append((x,mathFunc(x)))
    return answer

def getDistance(xdata, ydata, point):
    compareX, compareY = None, None
    for i in xrange(1,len(xdata)):
        x = xdata[i]
        if x > point[0]:
            x1,y1 = xdata[i-1],ydata[i-1]
            x2,y2 = xdata[i],ydata[i]
            compareX = point[0]
            compareY = fitBackend.interpolate(x1,y1,x2,y2,compareX)
            break
    if compareX == None: return float('inf')
    diffx = point[0] - float(compareX)
    diffy = point[1] - float(compareY)
    return (diffx**2 + diffy**2)**.5

#mathFunc(x) spits out y
# useExtrema - boolean
# loLimit, hiLimit - defines domain
# step - size of step when looking for extrema
# additionalX - additional critical points too look at
def criticalPointGrader(xdata, ydata, mathFunc, useExtrema, loLimit, hiLimit, step, maxDist, additionalX=[]):
    # construct list of critical points
    criticalPoints = []
    if useExtrema:
        criticalPoints.extend(getLocalExtrema(mathFunc, loLimit, hiLimit, step))
    for x in additionalX:
        criticalPoints.append((x,mathFunc(x)))
    
    grade = 100
    for (x,y) in criticalPoints:
        if getDistance(xdata, ydata, (x,y)) > maxDist:
            grade -= 100./len(criticalPoints)
    return grade
    

def findBadOnes(graphIndex, (answerType, answerParams)):
    print "\n\n\n Grading index",graphIndex
    noneData = []
    for x in xrange(1,240):
        d = fitBackend.getArrayData(x, graphIndex)
        if d == None:
            noneData.append(x)
            continue
        xdata, ydata = d
        grade,reasons = curveGrader(xdata, ydata, (answerType, answerParams))
        if grade < 100:
            print "studentID:",x,"graphIndex:",graphIndex,"grade:",grade,"reasons:",reasons
    print "None data in these indices",noneData
    print "done looking through grades"


def passingGrade(humanGrade, computerGrade):
    return (humanGrade > 60) == (computerGrade > 60)

# answers is a dictionary of following form:
# {(studentID, graphIndex),(grade,'comments')
# agreementFunction(humanGrade, computerGrade) 
#      returns True if human and computer agree
def curveGradeWithStats(answers, graphIndex, (answerType, answerParams), agreementFunc = passingGrade):
    agreements = [] # grades agree humans computers
    highHuman = [] # human grade higher than computer's
    highComputer = [] # human grade lower than computer's
    for k in answers.keys():
        if k == 'kerberos':
            continue
        (studentID, index) = k
        if index != graphIndex:
            continue
        humanGrade = answers[k]
        humanGrade = float(humanGrade)
        d = fitBackend.getArrayData(studentID, graphIndex)
        xdata, ydata = d
        computerGrade, reasons = curveGrader(xdata, ydata, (answerType, answerParams))
        #if grade above 50, consider as 100%
        if agreementFunc(humanGrade, computerGrade):
            agreements.append((studentID, graphIndex))
        elif humanGrade > computerGrade:
            highHuman.append((studentID, graphIndex))
        else:
            highComputer.append((studentID, graphIndex))
    return {'agreements':agreements, 'highHuman':highHuman, 'highComputer':highComputer}

def criticalPointGradeWithStats(answers, graphIndex, mathFunc, useExtrema, lo, hi, step, maxDist, addX = [], agreementFunc = passingGrade):
    agreements = [] # grades agree humans computers
    highHuman = [] # human grade higher than computer's
    highComputer = [] # human grade lower than computer's
    for k in answers.keys():
        if k == 'kerberos':
            continue
        (studentID, index) = k
        if index != graphIndex:
            continue
        humanGrade = answers[k]
        humanGrade = float(humanGrade)
        d = fitBackend.getArrayData(studentID, graphIndex)
        xdata, ydata = d
        computerGrade = criticalPointGrader(xdata, ydata, mathFunc, useExtrema, lo, hi, step, maxDist, addX)
        #if grade above 50, consider as 100%
        if agreementFunc(humanGrade, computerGrade):
            agreements.append((studentID, graphIndex))
        elif humanGrade > computerGrade:
            highHuman.append((studentID, graphIndex))
        else:
            highComputer.append((studentID, graphIndex))
    return {'agreements':agreements, 'highHuman':highHuman, 'highComputer':highComputer}


def createAndSaveScatter(humanGrades, computerGrades, filename):
    plt.scatter(humanGrades, computerGrades);
    plt.savefig(filename + '.png')

def curveGradeAndSavePlot(answers, graphIndex, (answerType, answerParams), filename):
    humanGrades = []
    computerGrades = []
    for k in answers.keys():
        if k == 'kerberos':
            continue
        (studentID, index) = k
        if index != graphIndex:
            continue
        humanGrade = answers[k]
        humanGrade = float(humanGrade)
        d = fitBackend.getArrayData(studentID, graphIndex)
        xdata, ydata = d
        computerGrade, reasons = curveGrader(xdata, ydata, (answerType, answerParams))
        humanGrades.append(humanGrade)
        computerGrades.append(computerGrade)
    createAndSaveScatter(humanGrades, computerGrades, filename)

def criticalGradeAndSavePlot(answers, graphIndex, mathFunc, useExtrema, lo, hi, step, maxDist, addX, filename):
    humanGrades = []
    computerGrades = []
    for k in answers.keys():
        if k == 'kerberos':
            continue
        (studentID, index) = k
        if index != graphIndex:
            continue
        humanGrade = answers[k]
        humanGrade = float(humanGrade)
        d = fitBackend.getArrayData(studentID, graphIndex)
        xdata, ydata = d
        computerGrade = criticalPointGrader(xdata, ydata, mathFunc, useExtrema, lo, hi, step, maxDist, addX)
        humanGrades.append(humanGrade)
        computerGrades.append(computerGrade)
    createAndSaveScatter(humanGrades, computerGrades, filename)



def gradesCloseBy(humanGrade, computerGrade):
    return abs(humanGrade - computerGrade) < 5

# grade with Stats
answerAgg = dataFuncs.getAggregateResponses()

'''for (graphIndex, (answerType, answerParams)) in [(0, (0,(1,2,-4,0))),\
        (1,(1,(1.1,3.14/4., 0))), (3, (0,(0,0,.5,0))), (4, (0,(0,1,0,0))),\
        (5,(2,(1,0,0)))]:
    results = gradeWithStats(answerAgg, graphIndex, (answerType, answerParams), gradesCloseBy)
    agree = len(results['agreements'])
    highHum = len(results['highHuman'])
    highComp = len(results['highComputer'])
    total = agree + highHum + highComp
    print agree, highHum, highComp, total
    print results['highHuman'], results['highComputer']
'''

# scatter plots
'''for (graphIndex, (answerType, answerParams), filename) in [(0, (0,(1,2,-4,0)), 'cubic'),\
        (1,(1,(1.1,3.14/4., 0)),'sinusoid'), (3, (0,(0,0,.5,0)),'linear'), (4, (0,(0,1,0,0)),'parabola'),\
        (5,(2,(1,0,0)),'absolute')]:
    gradeAndSavePlot(answerAgg, graphIndex, (answerType, answerParams), filename)'''

'''for (graphIndex, mathFunc, useExtrema, lo, hi, step, maxDist, addX) in [\
      (0, lambda x:fitBackend.poly3(x,1,2,-4,0), True, -3, 2., .1, 2.5, []),\
      (1, lambda x:fitBackend.sinusoid(x,1.1,3.14/4.,0.), True, 0., 20., .1, 2.5, []),\
      (3, lambda x:fitBackend.poly3(x,0,0,.5,0), False, 0,0,0.1, 2.5, [-2,0,2]), \
      (4, lambda x:fitBackend.poly3(x,0,1,0,0), True,-2,2,.1, 2.5, [-3,-2,-1,0,1,2,3])\
      ]:
    results = criticalPointGradeWithStats(answerAgg, graphIndex, mathFunc, useExtrema, lo, hi, step, maxDist, addX, agreementFunc = gradesCloseBy)
    agree = len(results['agreements'])
    highHum = len(results['highHuman'])
    highComp = len(results['highComputer'])
    total = agree + highHum + highComp
    print agree, highHum, highComp, total
    print results['highHuman'], results['highComputer']'''

for (graphIndex, mathFunc, useExtrema, lo, hi, step, maxDist, addX, filename) in [\
      (0, lambda x:fitBackend.poly3(x,1,2,-4,0), True, -3, 2., .1, 2.5, [], 'criticalCubic'),\
      (1, lambda x:fitBackend.sinusoid(x,1.1,3.14/4.,0.), True, 0., 20., .1, 2.5, [],'criticalSinusoid'),\
      (3, lambda x:fitBackend.poly3(x,0,0,.5,0), False, 0,0,0.1, 2.5, [-2,0,2], 'criticalLinear'), \
      (4, lambda x:fitBackend.poly3(x,0,1,0,0), True,-2,2,.1, 2.5, [-3,-2,-1,0,1,2,3], 'criticalParabola')\
      ]:
    criticalGradeAndSavePlot(answerAgg, graphIndex, mathFunc, useExtrema, lo, hi, step, maxDist, addX, filename)

'''results = criticalGradeAndSavePlot(answerAgg, 0, lambda x:fitBackend.poly3(x,1,2,-4,0), True, -3., 2., .1, 2.5, [], 'criticalParabola')
'''
