#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  2 12:55:41 2020

@author: enriquem
"""


# For pyWooby
import sys
import os
pyWoobyPath =  os.path.join(os.path.split(os.getcwd())[0])
sys.path.append(pyWoobyPath)
from pyWooby import Wooby
import pyWooby

import numpy as np
import matplotlib.pyplot as plt


## Initializing the Wooby element
myWooby = Wooby()

# Reading of the file
# fileFolder = os.path.join(os.getcwd(), "datasets", "VccMeasurement")
# fileName = "VccMeasurement_500gr_500gr.txt"


fileFolder = os.path.join(pyWoobyPath, "datasets", "VccAnalysis_Vader")
fileName = "essai.csv"


WoobyVccStudy = pyWooby.load.readWoobyFile(fileFolder, fileName, verbose=False)

WoobyDFVccStudyRaw = WoobyVccStudy["data"]

## Completing calculations
WoobyDFVccStudy = myWooby.extraCalcWooby(WoobyDFVccStudyRaw)

### Vcc analysis
if "timeSim" in WoobyDFVccStudy:
    timeSimKey = "timeSim" 
    timeNormKey = "timeNorm"
elif "timeSim1" in WoobyDFVccStudy:
    timeSimKey = "timeSim1" 
    timeNormKey = "timeNorm1"
else:
    raise Exception('The fields of the file are not suficient to run the Vcc analysis')
    
    

Vccref = 3;

tout, vccFiltered = pyWooby.filtering.filter_1od(WoobyDFVccStudy[timeSimKey]/1000, WoobyDFVccStudy["vccVolts"], 10, 0.7)
ratio = pyWooby.filtering.mapval(vccFiltered, 5.0, 7.4, 0, 1) 

timeVcc = np.array(WoobyDFVccStudy[timeNormKey]/1000/60/60)
# Plot: Vcc vs time
plt.figure()
plt.plot(timeVcc, WoobyDFVccStudy["vccVolts"], label ="vccVolts")
#plt.plot(tout, vccFiltered, label ="Filtered")
#plt.plot(tout, ratio*100, label ="Filtered")
plt.plot([timeVcc[0], timeVcc[-1]], [Vccref, Vccref], 'k--')
plt.show()
plt.grid(True)
plt.legend(loc='best')
plt.title("Vcc plot")
plt.ylabel("Vcc (Volts)")
plt.xlabel("Time normalized (hours) ")

# Calculation of the actual ON time
np.array(WoobyDFVccStudy[WoobyDFVccStudy["vccVolts"]>Vccref][timeNormKey])[-1]/1000/60/60

