import ast
import linecache

pathToGraphData = r'data/graphData.txt'
pathToResponseData = r'data/responseData.txt'
pathToInstructionData = r'data/instructions.html'
pathToAnswerPlotData = r'data/answerPlotData.txt'
pathToAggregateResponses = r'data/responseAggregate.txt'

def aggregateResponses():
    agg = {}
    f = open(pathToResponseData,'r')
    for line in f:
        rep = ''
        #try:
        #rep = ast.literal_eval(line[:-1])
        #except:
         #   pass
        if line[-1] == "\n":
            line = line[:len(line)-1]
        try:
            rep = ast.literal_eval(line)
        except:
            rep = {}
        if type(rep) == dict:
            #iterate through all responses in dictionary
            if len(rep) == 0:
                continue
            kerberos = rep['kerberos']
            print kerberos
            for key in rep.keys():
                if key == 'kerberos':
                    continue
                try:
                    float(rep[key][0])
                except:
                    continue
                if key in agg:
                    agg[key].append(float(rep[key][0]))
                else:
                    agg[key] = [float(rep[key][0])]
    for key in agg:
        agg[key] = sum(agg[key])/len(agg[key]) #average
    f.close()
    g = open(pathToAggregateResponses, 'w')
    g.write(str(agg))
    g.close()

def getAggregateResponses():
    f = open(pathToAggregateResponses, 'r')
    rep = ast.literal_eval(f.read())
    f.close()
    return rep



#aggregateResponses()

def getGraphData(studentID, graphIndex):
    line = linecache.getline(pathToGraphData, studentID)
    if line == "":
        return None
    if line[-1] == "\n":
        line = line[:len(line)-1]
    try:
        rep = ast.literal_eval(line)
    except:
        print "Error in getting graph data"
    if graphIndex < len(rep):
        return rep[graphIndex]
    else:
        return None

def getPrevNextGraphData(curStudentID, curGraphIndex):
    (prevStudentID, prevGraphIndex, nextStudentID, nextGraphIndex) = (curStudentID, curGraphIndex, curStudentID, curGraphIndex)
    ID = curStudentID
    gIndex = curGraphIndex + 1
    while ID < 300:
        while gIndex <= 5:
            gData = getGraphData(ID, gIndex)
            if gData != None and gData != "":
                (nextStudentID, nextGraphIndex) = (ID, gIndex)
                break
            gIndex += 1
        if nextStudentID != curStudentID or nextGraphIndex != curGraphIndex:
            break
        ID += 1
        gIndex = 0

    ID = curStudentID
    gIndex = curGraphIndex - 1
    while ID >= 0:
        while gIndex >= 0:
            gData = getGraphData(ID, gIndex)
            if gData != None and gData != "":
                (prevStudentID, prevGraphIndex) = (ID, gIndex)
                break
            gIndex -= 1
        if (prevStudentID != curStudentID or prevGraphIndex != curGraphIndex):
            break
        ID -= 1
        gIndex = 5
    return ((prevStudentID, prevGraphIndex),(nextStudentID, nextGraphIndex))

def getNextUngradedGraphIDs(kerberos, curStudentID, curGraphIndex):
    responses = getResponseData(kerberos)
    ID = curStudentID
    gIndex = curGraphIndex + 1
    while ID < 300:
        while gIndex <= 5:
            gData = getGraphData(ID, gIndex)
            if gData != None and gData != "" and (ID, gIndex) not in responses:
                return (ID, gIndex)
            gIndex += 1
        ID += 1
        gIndex = 0
    return (curStudentID, curGraphIndex)

def getPrevUngradedGraphIDs(kerberos, curStudentID, curGraphIndex):
    responses = getResponseData(kerberos)
    ID = curStudentID
    gIndex = curGraphIndex + 1
    while ID >= 0:
        while gIndex >= 0:
            gData = getGraphData(ID, gIndex)
            if gData != None and gData != "" and (ID, gIndex) not in responses:
                return (ID, gIndex)
            gIndex -= 1
        ID -= 1
        gIndex = 5
    return (curStudentID, curGraphIndex)


#string data will be formatted like this
#{'kerberos': 'martelly', (studentID, graphIndex) : (grade, comments)}
def getResponseData(kerberos):
    try:
        f = open(pathToResponseData, 'r')
    except:
        return {"kerberos":kerberos}
    ans = None
    for line in f:
        if line[-1] == "\n":
            line = line[:len(line)-1]
        try:
            rep = ast.literal_eval(line)
        except SyntaxError:
            rep = None
        if rep != None and rep["kerberos"] == kerberos:
            ans = rep
            break
    f.close()
    if ans == None:
        return {"kerberos":kerberos}
    else:
        return ans

# studentID will be the line number of the text file
# graphIndex should be between 0 and 4
# returns (grade, comments)
def getResponse(kerberos, studentID, graphIndex):
    rep = getResponseData(kerberos)
    return rep.get((studentID, graphIndex), ("",""))


def saveResponse(kerberos, studentID, graphIndex, grade, comments):
    try:
        f = open(pathToResponseData, "r")
        lines = f.readlines()
        f.close()
    except:
        lines = []
    rep = None
    for i in range(len(lines)):
        line = lines[i]
        if line[-1] == "\n":
            line = line[:len(line)-1]
        try:
            rep = ast.literal_eval(line)
        except SyntaxError:
            rep = None
        except:
            pass
        if rep != None and rep["kerberos"] == kerberos:
            lines.pop(i)
            break
    if rep == None or rep["kerberos"] != kerberos:
        rep = {"kerberos":kerberos}
    if rep.get((studentID, graphIndex)) == (grade, comments):
        return
    rep[(studentID, graphIndex)] = (grade, comments)
    lines.insert(0, str(rep) + "\n")
    f = open(pathToResponseData, 'w')
    lines = "".join(lines)
    f.write(lines)
    f.close()

def getInstructionText():
    f = open(pathToInstructionData)
    text = f.read()
    f.close()
    return text

def getAnswerPlotData(graphIndex):
   return linecache.getline(pathToAnswerPlotData, graphIndex+1) 
