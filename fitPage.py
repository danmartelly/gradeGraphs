#!/usr/bin/python
import dataFuncs
import fitBackend
import os
import cgi
import cgitb
cgitb.enable()

user = os.environ.get('SSL_CLIENT_S_DN_Email','').split('@')[0].strip()
fullname = os.environ.get('SSL_CLIENT_S_DN_CN',user)

studentID = 1 
graphIndex = 0
queryString = os.environ.get('QUERY_STRING','')
queries = queryString.split('&')
for query in queries:
    q = query.split('=')
    if q[0] == 'studentID':
        try:
            studentID = int(q[1])
        except:
            pass
    if q[0] == 'graphIndex':
        try:
            graphIndex = int(q[1])
        except:
            pass

data = dataFuncs.getGraphData(studentID, graphIndex)
answerData = dataFuncs.getAnswerPlotData(graphIndex)

functionLatex = ""
eq = ["y = x^3 + 2x^2 - 4x", r"y = 1.1^x\sin(\frac{\pi x}{4})",\
	"", r"y = \frac{x}{2}", r"y = x^2", r"y = |x|"][graphIndex]
if eq != "":
    functionLatex = r'<img src="http://latex.codecogs.com/gif.latex?%s" border="0"/>' % eq

curveResults = fitBackend.tryFits(studentID, graphIndex)
curveString = ""
fNames = ['cubic', 'sinusoid', 'absolute']
bestIndex = 0
for i in range(len(curveResults)):
    (popt, fres) = curveResults[i]
    curveString += fNames[i if i < len(fNames) else 0] + " " + str(list(popt)) 
    curveString += " Residuals squared: " + str(fres)
    curveString += "<br>"
    if fres >= 0 and fres < curveResults[bestIndex][1]:
        bestIndex = i

f = None
fitData = []
(popt, fres) = curveResults[bestIndex]
if bestIndex == 0:
    f = lambda x: fitBackend.poly3(x, popt[0],popt[1],popt[2],popt[3]);
elif bestIndex == 1:
    f = lambda x: fitBackend.sinusoid(x, popt[0],popt[1],popt[2])
elif bestIndex == 2:
    f = lambda x: fitBackend.absolute(x, popt[0],popt[1],popt[2])

domain = [[-3.5,2.5],[0,20],[0,20],[-5,5],[-3,3],[-5,5]][min(graphIndex,5)]

fitData = fitBackend.generatePoints(f, domain[0], domain[1], .1)
fitData = str(fitData) 
fitData = '{"data":'+fitData+',"color":"rgb(0,0,0)"}'

#(grade, comments) = dataFuncs.getResponse(user, studentID, graphIndex)
error = ""
#handle form
((prevID, prevIndex),(nextID, nextIndex)) = dataFuncs.getPrevNextGraphData(studentID, graphIndex)

#normal page content
print '''
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
	<title>Graph fit</title>
	<script language="javascript" type="text/javascript" src="flot/jquery.js"></script>
	<script language="javascript" type="text/javascript" src="flot/jquery.flot.js"></script>
	<script type="text/javascript">

	$(function() {

		var data = [%(answerData)s, %(fitData)s, %(data)s];

		$.plot("#placeholder", data);
	});

	removeSaveFeedback = function() {
                console.log("hi");
		$("#saveFeedback").text('');
	}

	$("#gradeInput").on('change', removeSaveFeedback);

	</script>
</head>
<body>

	<div id="content" style="float:left;">
	    <div id="placeholder" style="width:400px;height:300px;"></div>
	    <div style="height:50px">%(functionLatex)s</div>
	    <div>
		%(curveString)s
	    </div>
            <a href="?studentID=%(prevID)s&graphIndex=%(prevIndex)s">go to prev</a>
	    <a href="?studentID=%(nextID)s&graphIndex=%(nextIndex)s">go to next</a>
	</div>
<!--Errors:%(error)s>
</body>
</html>
''' % {"data": data, 'answerData':answerData, "user":user, \
'fitData':fitData, 'error':error, \
'prevID':prevID, 'prevIndex':prevIndex, 'nextID':nextID, 'nextIndex':nextIndex, \
'functionLatex':functionLatex, 'curveString':curveString}
