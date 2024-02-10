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
import pandas as pd
import matplotlib.pyplot as plt


## Initializing the Wooby element
myWooby = Wooby()

# Reading of the file
# fileFolder = os.path.join(os.getcwd(), "datasets", "VccMeasurement")
# fileName = "VccMeasurement_500gr_500gr.txt"


# Reading with pyWooby file
fileFolder = os.path.join(pyWoobyPath, "datasets", "VccAnalysis_Vader")
fileName = "essai.csv"
WoobyVccStudy = pyWooby.load.readWoobyFile(fileFolder, fileName, verbose=False)
WoobyDFVccStudyRaw = WoobyVccStudy["data"]


## Reading with external file
fileFolder = os.path.join(pyWoobyPath, "datasets", "VccAnalysis_Vader")

# For discharge
#fileName = "capture.txt"
fileName_1 = "full_discharge_2.txt"
fileName_2 = "full_discharge_3.txt"
WoobyDFVccStudyRaw_1 = myWooby.process_file(os.path.join(fileFolder, fileName_1))
WoobyDFVccStudyRaw_2 = myWooby.process_file(os.path.join(fileFolder, fileName_2))

WoobyDFVccStudyRaw_2["tBeforeMeasure1"] = WoobyDFVccStudyRaw_2["tBeforeMeasure1"] + WoobyDFVccStudyRaw_1["tBeforeMeasure1"].iloc[-1]
WoobyDFVccStudyRaw_2["tAfterMeasure1"] = WoobyDFVccStudyRaw_2["tAfterMeasure1"] + WoobyDFVccStudyRaw_1["tAfterMeasure1"].iloc[-1]

WoobyDFVccStudyRaw = pd.concat([WoobyDFVccStudyRaw_1, WoobyDFVccStudyRaw_2], ignore_index=True)

# For charge
fileName = "capture_charge.txt"
WoobyDFVccStudyRaw = myWooby.process_file(os.path.join(fileFolder, fileName))

fileNameRefCharge = "charge_reference.csv"
referenceCharge = pd.read_csv(os.path.join(fileFolder, fileNameRefCharge), sep=";")
referenceCharge = referenceCharge.fillna(0)
referenceCharge["Time total [h]"] = referenceCharge["Time [h]"] +   referenceCharge["Time [m]"]/60 +   referenceCharge["Time [s]"]/60/60 ;

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

# Filtering of the Vcc data
timeConstantFilter = 10         # in s
tout, vccFiltered = pyWooby.filtering.filter_1od(WoobyDFVccStudy[timeSimKey]/1000, WoobyDFVccStudy["vccVolts"], timeConstantFilter, (WoobyDFVccStudy[timeSimKey][1]-WoobyDFVccStudy[timeSimKey][0])/1000)
ratio = pyWooby.filtering.mapval(vccFiltered, 3.0, 4.2, 0, 1) 

timeVcc = np.array(WoobyDFVccStudy[timeSimKey]/1000/60/60)
# Plot: Vcc vs time
plt.figure()
plt.plot(timeVcc, WoobyDFVccStudy["vccVolts"], 'o-', label ="vccVolts")
plt.plot(timeVcc, WoobyDFVccStudy["vccReadVolts"], '-', label ="vccReadVolts")
plt.plot(tout/60/60, vccFiltered, label ="Filtered")
#plt.plot(tout, ratio*100, label ="Filtered")
plt.plot(referenceCharge["Time total [h]"], referenceCharge["Measured voltage [V]"], 'ko--')
plt.plot([timeVcc[0], timeVcc[-1]], [Vccref, Vccref], 'k--')
plt.show()
plt.grid(True)
plt.legend(loc='best')
plt.title("Vcc plot - ")
plt.ylabel("Vcc (Volts)"  )
plt.xlabel("Time normalized (hours) ")
plt.ylim([0.95*Vccref, 1.05*np.max(WoobyDFVccStudy["vccVolts"])])

# Calculation of the actual ON time
np.array(WoobyDFVccStudy[WoobyDFVccStudy["vccVolts"]>Vccref][timeNormKey])[-1]/1000/60/60

# Support plots (for timing)

plt.figure()
xData = WoobyDFVccStudyRaw.timeSim1/1000/60/60;
xData = timeVcc;
plt.plot(xData, xData, 'o--')
plt.show()
plt.grid(True)


