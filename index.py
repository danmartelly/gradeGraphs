#!/usr/bin/python
import dataFuncs
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
instructions = dataFuncs.getInstructionText()
#(grade, comments) = dataFuncs.getResponse(user, studentID, graphIndex)
error = ""
#handle form
form = cgi.FieldStorage()
((prevID, prevIndex),(nextID, nextIndex)) = dataFuncs.getPrevNextGraphData(studentID, graphIndex)
(ungradedID, ungradedIndex) = dataFuncs.getNextUngradedGraphIDs(user, studentID, graphIndex)

(grade, comments) = dataFuncs.getResponse(user, studentID, graphIndex)
if form.has_key('grade') or form.has_key('comments'):
    if form.has_key('grade'): grade = form['grade'].value
    if form.has_key('comments'): comments = form['comments'].value
    dataFuncs.saveResponse(user, studentID, graphIndex, grade, comments)

numberGraded = len(dataFuncs.getResponseData(user)) - 1
thanksText = ""
if numberGraded == 0:
    thanksText = "Don't be scared to enter a grade"
elif numberGraded <= 3:
    thanksText = "This isn't so hard. Right?"
elif numberGraded <= 10:
    thanksText = "You're getting pretty good at this."
elif numberGraded <= 15:
    thanksText = "I'll keep you entertained with a few puns."
elif numberGraded <= 18:
    thanksText = "Why can't a bicycle stand up?....."
elif numberGraded <= 22:
    thanksText = "...Because it's too/2 tired."
elif numberGraded <= 25:
    thanksText = "What do you call a seagull flying around a bay?....."
elif numberGraded <= 27:
    thanksText = "...A bagel!"
elif numberGraded <= 29:
    thanksText = "A man just assaulted me with milk, cream, and butter. How dairy."
elif numberGraded <= 34:
    thanksText = "When the window fell into the incinerator, it was a pane in the ash to retrieve"
elif numberGraded <= 40:
    thanksText = "I'm out of jokes. Would you like to hear about my MEng thesis?"
elif numberGraded <= 42:
    thanksText = "Well, I'm going to tell you anyways"
elif numberGraded <= 44:
    thanksText = "Basically..."
elif numberGraded <= 45:
    thanksText = "We think interpreting and drawing graphs is a very useful skill for engineers and scientists."
elif numberGraded <= 47:
    thanksText = "Drawing a graph generally requires a deeper understanding of a system so it's a good opportunity for students to learn."
elif numberGraded <= 49:
    thanksText = "Grading a correct graph should be easy enough. Just check if the graph lies close enough to the answer graph."
elif numberGraded <= 51:
    thanksText = "The hard part about this project (in my opinion) is giving good, helpful, not frustrating feedback when a graph has been drawn incorrectly."
elif numberGraded <= 53:
    thanksText = "I've only just started working on it so I don't know what approach will work yet."
elif numberGraded <= 57:
    thanksText = "I trunly appreciate all the grading you're doing for me." 
else:
    thanksText = "Unfortunately, I've run out of clever things to say. Thank you so much though!"

#normal page content
saveFeedback = ""
if form.has_key('saveAndGo'):
    print 'Location: ?studentID=%(ungradedID)s&graphIndex=%(ungradedIndex)s'\
         % {'ungradedID': ungradedID, 'ungradedIndex': ungradedIndex}
elif form.has_key('save'):
    saveFeedback = "response saved"
print '''
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
	<title>Grade Graphs Please</title>
	<script language="javascript" type="text/javascript" src="flot/jquery.js"></script>
	<script language="javascript" type="text/javascript" src="flot/jquery.flot.js"></script>
	<script type="text/javascript">

	$(function() {

		var data = [%(answerData)s, %(data)s];

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
You are %(user)s. You've graded %(numberGraded)d. %(thanksText)s
<div>
	<div id="content" style="float:left;">
	    <div id="placeholder" style="width:400px;height:300px;"></div>
	    <div style="height:50px">%(functionLatex)s</div>
            <form name="grading" method=POST>
		Grade: <input id="gradeInput" name="grade" type="number" value="%(grade)s">
		<br>Comments: <input id="commentsInput" name="comments" type="text" value="%(comments)s">
		<br>
		<input type="submit" name="save" value="Save Response">
		<input type="submit" name="saveAndGo" value="Save and go to next ungraded">
	        <p id="saveFeedback">%(saveFeedback)s<p>
	    </form>
	    <a href="?studentID=%(prevID)s&graphIndex=%(prevIndex)s">go to prev</a>
	    <a href="?studentID=%(ungradedID)s&graphIndex=%(ungradedIndex)s">go to next ungraded</a>
	    <a href="?studentID=%(nextID)s&graphIndex=%(nextIndex)s">go to next</a>
	</div>
	
	<div id="instructions" style="float:left;">
		%(instructions)s

	</div>
</div>
<!--Errors:%(error)s>
</body>
</html>
''' % {"data": data, 'answerData':answerData, "user":user, "grade":grade, \
"comments":comments, 'instructions':instructions, 'error':error, \
'prevID':prevID, 'prevIndex':prevIndex, 'nextID':nextID, 'nextIndex':nextIndex, \
'ungradedID':ungradedID, 'ungradedIndex':ungradedIndex, 'functionLatex':functionLatex,\
'saveFeedback':saveFeedback, 'numberGraded':numberGraded, 'thanksText':thanksText}
