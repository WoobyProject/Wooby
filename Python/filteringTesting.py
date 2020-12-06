#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  1 21:10:09 2020

@author: enriquem
"""

import sys
sys.path.append('../pyWooby')
import pyWooby

from scipy import signal

##################################        
#       Loading file             #
##################################

fileFolder = "/Users/macretina/Documents/Airbus/Humanity Lab/Wooby/Github/Python/datasets/Austin"
fileName = "Austin_104gr_Measure1.txt"
fileName = "Austin_104gr_Up_Box_Empty.txt"

WoobyData = pyWooby.load.readWoobyFile(fileFolder, fileName, verbose=True)
WoobyData = extraCalculationWooby(WoobyData)

WoobyDataFrame = WoobyData["data"]

##################################        
#      Filtering                 #
##################################


### Basic signal calculations
time = np.array(WoobyDataFrame["timeSim"])/1000
inputSignal =  np.array(WoobyDataFrame["realValue"])
# inputSignal =  0+(time>10) # np.ones(time.shape)


### First-order filter
tauFilter = -0.7/math.log(0.6085)
Te =  time[1] -  time[0]
t_out, resultFilter = pyWooby.filtering.filter_1od(time, inputSignal,  tauFilter,  Te)


### Discrete first-order filter equivalent 
b1 = 1 - math.exp(-Te/tauFilter)
a1 = math.exp(-Te/tauFilter)
    
b = np.atleast_1d(np.array((0, 0.3915)))
a = np.atleast_1d(np.array((1, -0.6085)))
resultFilterDiscrete, _ = signal.lfilter(b, a, inputSignal, zi=np.array([inputSignal[0]]))


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



### Comparison of filtering in different ways
plt.figure()
plt.plot(time, inputSignal, '--',       label="Input signal")
plt.plot(time, resultFilterDiscrete,    label="Discrete filter")
plt.plot(time, resultFilter,            label="First order filter")
plt.legend(loc="best")
plt.grid(True)


plt.figure()
plt.plot(time,WoobyDataFrame["realValue_WU"])
plt.grid(True)



