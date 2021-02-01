#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 10 18:30:55 2020

@author: enriquem
"""

fileFolder = os.path.join(os.getcwd(), "datasets", "UNITARY_TEST")
fileFilter = ""

unityTestResults = readWoobyFolder(fileFolder, fileFilter)


histUnit = plt.figure()
plotUnit = plt.figure()
lineUnit = plt.figure()

'''
condensed = WoobyDataFrame["realValue"].append(WoobyDataFrame["realValueFiltered"]).append(WoobyDataFrame["correctedValueFiltered"])
minVal = math.floor(min(condensed)) 
maxVal = math.ceil(max(condensed))
'''
bins = np.arange(42700, 43000, 25)

for i, element in enumerate(unityTestResults):
    unityTestResults[i] = calculationWooby(element)
    
    plt.figure(plotUnit.number)
    plt.plot(element["data"]["relativeValue_WU"], label=element["name"])
    
    plt.figure(histUnit.number)
    plt.hist(element["data"]["relativeValue_WU"], bins=bins, alpha=0.5, ec='black', label=element["name"])
    
    plt.figure(lineUnit.number)
    if ("REF" in element["name"] ):
        marker = 'x'
        ms = 10
    else:
        marker = 'o'
        ms = 5
    
    # meanUnity = np.mean(element["data"]["relativeValue_WU"])
    meanUnity = np.mean(element["data"]["correctedValueFiltered"])
    
    # correctedValueFiltered relativeValue_WU
    plt.plot(meanUnity, meanUnity, marker=marker, ms=ms, ls ='', label=element["name"])
    # plt.plot(element["data"]["relativeValue_WU"], element["data"]["relativeValue_WU"], marker=marker, ms=ms, ls ='', label=element["name"])
    # plt.plot(element["data"]["correctedValueFiltered"], element["data"]["correctedValueFiltered"], marker=marker, ms=ms, ls ='', label=element["name"])
    
    
    
    print(element["name"])
  
plt.figure(plotUnit.number)
plt.legend(loc="best")
plt.show()

plt.figure(histUnit.number)
plt.legend(loc="best")
plt.show()

plt.figure(lineUnit.number)
plt.legend(loc="best")
plt.show()



