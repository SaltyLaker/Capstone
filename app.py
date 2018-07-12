from flask import Flask,render_template,request,redirect,session
import simplejson as json
import pygal
from pytrends.request import TrendReq
from datetime import datetime, timedelta
import csv
import numpy as np
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.neighbors import KNeighborsRegressor

app = Flask(__name__)

def train(currentKeywordsTrend, percentUSA, dateUSA, keyWords, trainingType):
	timeStemp, keywordsTrendUS = getKeyWordsData(keyWords, 'US')
	outputDate, truthUS, timeStemp, featureUS = fitKeyWordTruth(percentUSA, dateUSA, keyWords,keywordsTrendUS, timeStemp)
	XPred = np.matrix(currentKeywordsTrend)
	XPred = np.transpose(XPred)
	X = np.matrix(featureUS)
	Y = np.matrix(truthUS)
	X = np.transpose(X)
	Y = np.transpose(Y)
	mdl = None

	if trainingType == "linearRegression":
		mdl = LinearRegression().fit(X,Y)
	elif trainingType == "KNeighborsRegressor":
		mdl = KNeighborsRegressor().fit(X,Y)

	if mdl != None:
		predTrain = mdl.predict(XPred)
		predTrain = np.transpose(predTrain)[0]
		return predTrain

def outputData(keyWords, region, trainingType):
	targetKeyWord = keyWords

	dateUSA, percentUSA = getFlueData()

	timeStemp, keywordsTrend = getKeyWordsData(keyWords, region)

	outputDate, truth,timeStemp, keywordsTrend = fitKeyWordTruth(percentUSA, dateUSA, targetKeyWord,keywordsTrend, timeStemp)
	
	prediction = train(keywordsTrend, percentUSA, dateUSA, keyWords, trainingType)

	if region == 'US':
		outputkeyWords = ["CDC Data"] + ["Prediction"]+ keyWords
		outputData = [truth] + [prediction] + keywordsTrend
	else:
		outputkeyWords = ["Prediction"]+ keyWords
		outputData = [prediction] + keywordsTrend

	return outputkeyWords, outputDate, outputData


def fitKeyWordTruth(percentUSA, dateUSA, targetKeyWord,keywordsTrend, timeStemp):
	date = []
	truth = []

	feature = []
	for i in range(0,len(targetKeyWord)):
	    feature.append([])

	i = 0 #dateUSA
	j = 0 #timeStemp
	while( (i<len(dateUSA)) and (j<len(timeStemp))):
	    delta = (dateUSA[i] - timeStemp[j])/timedelta (days=1)
	    if (delta<=-7):
	        i = i+1
	    elif (delta>=7):
	        j = j+1
	    else:
	        date.append(timeStemp[j])
	        truth.append(percentUSA[i])
	        for k in range(0,len(targetKeyWord)):
	            feature[k].append(keywordsTrend[k][j])
	        i = i+1
	        j = j+1
	return date, truth, timeStemp, feature


def getFlueData():
	positiveUSA = []
	processedUSA = []
	percentUSA = []
	dateUSA = []
	with open('FluNetInteractiveReport.csv', 'r') as csv_file:#processing data in VT
	    csv_USA = csv.reader(csv_file)
	    
	    i = 0
	    
	    for line in csv_USA:
	        if i>=4 and i<878:
	            currentPositive = line[19]
	            currentProcessed = line[8]
	            currentDate = line[6]
	            
	            if currentPositive.isdigit() and currentProcessed.isdigit():
	                dateUSA.append(datetime.strptime(currentDate,'%Y-%m-%d'))
	                
	                positiveUSA.append((int)(currentPositive))
	                
	                processedUSA.append((int)(currentProcessed))
	                
	                currentPercent = (float)(currentPositive)/(float)(currentProcessed)*100
	                percentUSA.append(currentPercent)
	                
	                
	        #index
	        i = i+1 


	return dateUSA, percentUSA

def getKeyWordsData(keyWords, region):

	getFlueData()

	pytrend = TrendReq()

	#targetKeyWord = ['flu', 'fever', 'headache', 'cough']
	targetKeyWord = keyWords

	timeStemp = []
	keywordsTrend = []

	for i in range(0,len(targetKeyWord)):
	    keywordsTrend.append([])

	pytrend.build_payload(kw_list=targetKeyWord, geo = region)

	timeStempDataFrame = pytrend.interest_over_time()

	for i in range(0,len(timeStempDataFrame)):
	    timeStemp.append(datetime.utcfromtimestamp(timeStempDataFrame.index.values[i].tolist()/1e9))
	    for j in range(0,len(targetKeyWord)):
	        keywordsTrend[j].append(timeStempDataFrame.iat[i,j])
	return timeStemp, keywordsTrend

'''@app.route('/')
def main():
  return redirect('/index')

@app.route('/index', methods=['GET'])
def index():
    graph = pygal.Line()
	graph.title = '% Change Coolness of programming languages over time.'
	graph.x_labels = ['2011','2012','2013','2014','2015','2016']
	graph.add('Python',  [15, 31, 89, 200, 356, 900])
	graph.add('Java',    [15, 45, 76, 80,  91,  95])
	graph.add('C++',     [5,  51, 54, 102, 150, 201])
	graph.add('All others combined!',  [5, 15, 21, 55, 92, 105])
	graph_data = graph.render_data_uri()
	return render_template("graphing.html", graph_data = graph_data)'''


@app.route('/')
def main():
  return redirect('/index')

@app.route('/index', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/customGraph/')
def customGraph():
    return render_template('customGraph.html')

'''
def pygalexample():
	graph = pygal.Line()
	graph.title = '% Change Coolness of programming languages over time.'
	graph.x_labels = ['2011','2012','2013','2014','2015','2016']
	graph.add('Python',  [15, 31, 89, 200, 356, 900])
	graph.add('Java',    [15, 45, 76, 80,  91,  95])
	graph.add('C++',     [5,  51, 54, 102, 150, 201])
	graph.add('All others combined!',  [5, 15, 21, 55, 92, 105])
	graph_data = graph.render_data_uri()
	return render_template("index.html", graph_data = graph_data)'''

@app.route('/customGraph', methods=['POST'])
def customGraphPost():
	stockName = request.form.get('keyWord')
	region = request.form.get('region')
	keyWords = stockName.split()
	MLType = request.form.get('MLType')


	keyWords, timeStemp, keyWordData = outputData(keyWords, region, MLType)

	graph = pygal.Line()
	graph.title = 'Google Trend Keyword Data - ' + region
	graph.x_labels = timeStemp
	for i in range(len(keyWordData)):
		graph.add(keyWords[i],  keyWordData[i])
	graph_data = graph.render_data_uri()
	#return render_template("index.html", graph_data = graph_data)
	return render_template("customGraph.html", graph_data = '<embed type="image/svg+xml" src= ' + graph_data + ' style=''max-width:1000px''/>')
	#<embed type="image/svg+xml" src={{graph_data|safe}} style='max-width:1000px'/>

@app.route('/worldGraph/')
def worldGraph():
	worldmap_chart = pygal.maps.world.World()
	worldmap_chart.title = 'Flu Forcast'
	worldmap_chart.add('increase', ['us'])
	worldmap_chart.add('contain', ['gb', 'br'])
	worldmap_chart.add('decrease', ['in'])
	worldmap_chart.render()
	graph_data = worldmap_chart.render_data_uri()		
	#return render_template("index.html", graph_data = graph_data)
	return render_template("worldMap.html", graph_data = '<embed type="image/svg+xml" src= ' + graph_data + ' style=''max-width:1000px''/>')
	