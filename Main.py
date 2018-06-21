#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 13 17:17:50 2018

@author: parallels
"""

import csv
import matplotlib.pyplot as plt
import numpy as np

from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
from pytrends.request import TrendReq

positiveUSA = []
processedUSA = []
percentUSA = []
dateUSA = []

#read Clinical Data from csv file
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
        
pytrend = TrendReq()

#Read keyword from google trends
#Variable
targetKeyWord = ['fever', 'headache', 'cough']

timeStemp = []
keywordsTrend = []

for i in range(0,len(targetKeyWord)):
    keywordsTrend.append([])

# Create payload and capture API tokens. Only needed for interest_over_time(), interest_by_region() & related_queries()
pytrend.build_payload(kw_list=targetKeyWord, geo = 'US')

timeStempDataFrame = pytrend.interest_over_time()

for i in range(0,len(timeStempDataFrame)):
    timeStemp.append(datetime.utcfromtimestamp(timeStempDataFrame.index.values[i].tolist()/1e9))
    for j in range(0,len(targetKeyWord)):
        keywordsTrend[j].append(timeStempDataFrame.iat[i,j])
        
#plot
plt.plot(dateUSA[-250:-1], percentUSA[-250:-1]) #plot clinical data

#plot keyword data
for i in range(0,len(targetKeyWord)):   
    plt.plot(timeStemp, keywordsTrend[i])
    

plt.legend(['Truth'] + targetKeyWord)
plt.show()

#aline data
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
        
plt.plot(date, truth)   
for i in range(0,len(targetKeyWord)):   
    plt.plot(date, feature[i])
plt.legend(['Truth'] + targetKeyWord)
plt.show()

style = ['b.', 'm.', 'g.','r.']
for i in range(0,len(targetKeyWord)):   
    plt.plot(truth, feature[i],style[i])
    
plt.legend(targetKeyWord)

style = ['b', 'm', 'g','r']
for i in range(0,len(targetKeyWord)): 
    z = np.polyfit(truth, feature[i], 1)
    p = np.poly1d(z)
    plt.plot(truth,p(truth),style[i])
plt.show()

#derivative
truthDe = []
featureDe = []
for i in range(0,len(targetKeyWord)):
    featureDe.append([])
    
for i in range(0,len(truth)-1):
    truthDe.append(truth[i]-truth[i+1])
    for k in range(0,len(targetKeyWord)):
        featureDe[k].append(feature[k][i] - feature[k][i+1])
      
dateDe = date[0:(len(date)-1)]
plt.plot(dateDe, truthDe)   
for i in range(0,len(targetKeyWord)):   
    plt.plot(dateDe, featureDe[i])
plt.legend(['Truth'] + targetKeyWord)
plt.show()

style = ['b.', 'm.', 'g.','r.']
for i in range(0,len(targetKeyWord)):   
    plt.plot(truthDe, featureDe[i],style[i])
    
plt.legend(targetKeyWord)

style = ['b', 'm', 'g','r']
for i in range(0,len(targetKeyWord)): 
    z = np.polyfit(truthDe, featureDe[i], 1)
    p = np.poly1d(z)
    plt.plot(truthDe,p(truthDe),style[i])
plt.show()

#linear regression
X = np.matrix(feature)
Y = np.matrix(truth)
X = np.transpose(X)
Y = np.transpose(Y)
mdl = LinearRegression().fit(X[0:100],Y[0:100])
trainIndicator = np.ones((100,1))
predTrain = mdl.predict(X)
plt.plot(date, Y)
plt.plot(date, predTrain)
plt.plot(date[0:100], trainIndicator)
plt.legend(['Truth', 'Predict'])
plt.show()


    


    


        
    
