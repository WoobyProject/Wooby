#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  1 21:39:13 2021

@author: enriquem
"""

import sys
import os
pyWoobyPath =  os.path.join(os.path.split(os.getcwd())[0])
sys.path.append(pyWoobyPath)


from pyWooby import Wooby


## Initializing the Wooby element
myWooby = Wooby()


## Checking available serial ports
avlbSerPorts= myWooby.availableSerialPorts()
print(avlbSerPorts)


## Select the serial port 
port = "/dev/" +  avlbSerPorts[1]
 

## Setup serial connection 
myWooby.setupSerial(port, baudrate = 115200)

WoobyDataFrame = myWooby.read("SERIAL")
WoobyDataFrame = myWooby.readNTimes("SERIAL", 100)


## Completing calculations
WoobyDataFrame = myWooby.extraCalcWooby(WoobyDataFrame)


## Export 
fileFolder = "/Users/enriquem/Documents/HumanityLab/Wooby/Github/Python/datasets/WOOBY2_TEST_FLITERING"
fileName = "LowValueFiltering_4.txt"

myWooby.exportCSV(WoobyDataFrame, fileName, fileFolder, overwrite=False)
    


###############################

# Plots

import matplotlib.pyplot as plt


## Comparison for all the filters
fig, ax1 = plt.subplots()

color = 'tab:red'
ax1.set_xlabel('time (ms)')
ax1.set_ylabel('raw measure', color=color)
ax1.plot(WoobyDataFrame["timeNorm"]/1000, WoobyDataFrame["realValue_WU"],        color=color, marker ="+")
ax1.tick_params(axis='y', labelcolor=color)

ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

color = 'tab:blue'
ax2.set_ylabel('Filtered values', color=color)  # we already handled the x-label with ax1
ax2.plot(WoobyDataFrame["timeNorm"]/1000, WoobyDataFrame["realValue_WU_MovAvg"], color='grey',  marker ="+")
ax2.plot(WoobyDataFrame["timeNorm"]/1000, WoobyDataFrame["realValue_WU_Filt"],   color ='black', marker ="+")

ax2.tick_params(axis='y', labelcolor=color)

# relativeVal_WU
# realValue_WU_AngleAdj
# realValue_WU_MovAvg
# realValue_WU_Filt
# realValue
# realValueFiltered
# correctedValueFiltered'
       
ax3 = ax1.twinx()  # instantiate a thrid  axes that shares the same x-axis
color = 'tab:orange'
ax3.set_ylabel('bSync', color=color)  # we already handled the x-label with ax3
ax3.plot(WoobyDataFrame["timeNorm"]/1000, WoobyDataFrame["realValue"], color =color, marker ="+", linestyle="--")
ax3.plot(WoobyDataFrame["timeNorm"]/1000, WoobyDataFrame["correctedValueFiltered"], color="cyan", marker ="+", linestyle="--")
ax3.tick_params(axis='y', labelcolor=color)



ax4 = ax1.twinx()  # instantiate a thrid  axes that shares the same x-axis
color = 'tab:pink'
ax4.set_ylabel('bSync', color=color)  # we already handled the x-label with ax1
ax4.plot(WoobyDataFrame["timeNorm"]/1000, WoobyDataFrame["bSync"], color=color,  marker ="+")
ax4.tick_params(axis='y', labelcolor=color)



fig.tight_layout()  # otherwise the right y-label is slightly clipped
plt.grid()
plt.show()



# Comparison raw data and final displayed value


## Comparison for all the filters
fig, ax1 = plt.subplots()

color = 'tab:red'
ax1.set_xlabel('time (ms)')
ax1.set_ylabel('raw measure', color=color)
ax1.plot(WoobyDataFrame["timeNorm"]/1000, WoobyDataFrame["realValue_WU"],        color=color, marker ="+")
ax1.tick_params(axis='y', labelcolor=color)

ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

color = 'tab:blue'
ax2.set_ylabel('Filtered values', color=color)  # we already handled the x-label with ax1
ax2.plot(WoobyDataFrame["timeNorm"]/1000, WoobyDataFrame["correctedValueFiltered"], color=color,  marker ="+")
ax2.tick_params(axis='y', labelcolor=color)


fig.tight_layout()  # otherwise the right y-label is slightly clipped
plt.grid()
plt.show()



