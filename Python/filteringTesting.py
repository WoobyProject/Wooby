#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  1 21:10:09 2020

@author: enriquem
"""

##################################        
#       Loading file             #
##################################

fileFolder = "/Users/macretina/Documents/Airbus/Humanity Lab/Wooby/Github/Python/datasets/Austin"
fileName = "Austin_104gr_Measure1.txt"
fileName = "Austin_104gr_Up_Box_Empty.txt"

WoobyData = readWoobyFile(fileFolder, fileName, verbose=True)
WoobyData = extraCalculationWooby(WoobyData)

WoobyDataFrame = WoobyData["data"]

##################################        
#      Filtering                 #
##################################


### Basic signal calculations

time = np.array(WoobyDataFrame["timeSim"])/1000
inputSignal =  np.array(WoobyDataFrame["realValue"])

### First-order filter
tauFilter = 0.2
Te =  time[1] -  time[0]

resultFilter = filter_1od(time, inputSignal,  tauFilter,  Te)

### Moving average (macro-function)
n = 7
resultMA = movingAvg(inputSignal, n)

### Moving average (macro-function) RAW
n = 7
resultMA_Raw = movingAvg(np.array(WoobyDataFrame["realValue_WU"] - WoobyDataFrame["OFFSET"] ), n)
resultMA_Raw = resultMA_Raw/WoobyDataFrame["calibrationFactor"]


### Moving average (filter)
num = [1/n]*n
den = np.append([1], np.zeros(n-1))
resultMAWithFilter = genericFilter(time, inputSignal, num, den, Te)

##################################        
#      Plots: comparison         #
##################################

### Comparison of Moving Averages with different ways
plt.figure()
plt.plot(time, inputSignal,         label="Input signal")
plt.plot(time, resultMA,            label="Moving Avg")
plt.plot(time, resultMA_Raw,        '+-',label="resultMA_Raw")
plt.plot(resultMAWithFilter[0], resultMAWithFilter[1], '--', label="Moving Avg (with filter)")
plt.legend(loc="best")
plt.grid(True)


plt.figure()
plt.plot(time,WoobyDataFrame["realValue_WU"])
plt.grid(True)



