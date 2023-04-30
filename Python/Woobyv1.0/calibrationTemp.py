#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 21 22:19:03 2020

@author: enriquem
"""

import os
import re
import pandas as pd

# import pyWooby


fileFolder = os.path.join(os.getcwd(), "datasets", "TEMP_TEST")
fileFilter = "Base|Tray3|Tray4"
'''
fileFilter = "Tray"
fileFilter = "Base"
'''
WoobyDataFrameList = readWoobyFolder(fileFolder, fileFilter, verbose=True)

timeVsTempFig = plt.figure()
valVsTempFig = plt.figure()
accelsVsTime = plt.figure()

for WoobyStruct in WoobyDataFrameList:
    WoobyDataFrame = WoobyStruct["data"]
    
    myTmpDiff = np.diff(WoobyDataFrame["myTmp"])/WoobyDataFrame["timeNorm"][1:]
    # Plot: Temperature vs time
    plt.figure(timeVsTempFig.number)
    plt.plot(WoobyDataFrame["timeNorm"], WoobyDataFrame["myTmp"], label= WoobyStruct["name"])
    #plt.plot(WoobyDataFrame["timeNorm"][1:], myTmpDiff, label= WoobyStruct["name"])
    plt.show()
    plt.grid(True)
    
    plt.figure(accelsVsTime.number)
    plt.plot(WoobyDataFrame["timeNorm"], WoobyDataFrame["myAx"], label="Ax"+WoobyStruct["name"])
    plt.plot(WoobyDataFrame["timeNorm"], WoobyDataFrame["myAy"], label="Ay"+WoobyStruct["name"])
    plt.plot(WoobyDataFrame["timeNorm"], WoobyDataFrame["myAz"], label="Az"+WoobyStruct["name"])
    plt.legend(loc='best')
    plt.grid(True)
    plt.show()

    
    sense = np.sign( np.sum(WoobyDataFrame["myTmp"]-WoobyDataFrame["myTmp"][0]) )
    marker = "^" if sense > 0 else "v"
    
    # Plot: Temperature vs relativeVal_WU
    plt.figure(valVsTempFig.number)
    plt.plot(WoobyDataFrame["myTmp"], WoobyDataFrame["realValue_WU"]/42.7461, label= WoobyStruct["name"], linestyle='',marker=marker) # 
    #plt.plot(WoobyDataFrame["myTmp"], WoobyDataFrame["relativeVal_WU"]/42.7461, label= WoobyStruct["name"], linestyle='',marker=marker) # 
    #plt.plot(WoobyDataFrame["myTmp"], WoobyDataFrame["realValueFiltered"], label= WoobyStruct["name"], linestyle='',marker=marker) # 
    plt.show()
    plt.grid(True)

plt.figure(timeVsTempFig.number)
plt.legend(loc="best")
plt.xlabel("Temperature (C)")
plt.ylabel("Measurement (wu)")

plt.figure(valVsTempFig.number)
plt.xlabel("Temperature (C)")
plt.ylabel("Measurement (wu)")
plt.legend(loc="best")

plt.figure(accelsVsTime.number)
plt.legend(loc="best")

