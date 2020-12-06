#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  2 12:55:41 2020

@author: enriquem
"""


# For pyWooby
import sys
sys.path.append('../pyWooby')
import pyWooby

# Reading of the file
fileFolder = os.path.join(os.getcwd(), "datasets", "VccMeasurement")
fileName = "VccMeasurement_500gr_500gr.txt"
WoobyVccStudy = pyWooby.load.readWoobyFile(fileFolder, fileName, verbose=False)

WoobyDFVccStudy = WoobyVccStudy["data"]


### Vcc analysis
tout, vccFiltered = pyWooby.filtering.filter_1od(WoobyDFVccStudy["timeSim"]/1000, WoobyDFVccStudy["vccVolts"], 10, 0.7)
ratio = pyWooby.filtering.mapval(vccFiltered, 5.0, 7.4, 0, 1) 

timeVcc = np.array(WoobyDFVccStudy["timeNorm"]/1000/60/60)
# Plot: Vcc vs time
plt.figure()
plt.plot(timeVcc, WoobyDFVccStudy["vccVolts"], label ="vccVolts")
#plt.plot(tout, vccFiltered, label ="Filtered")
#plt.plot(tout, ratio*100, label ="Filtered")
plt.plot([timeVcc[0], timeVcc[-1]], [5, 5], 'k--')
plt.show()
plt.grid(True)
plt.legend(loc='best')
plt.title("Vcc plot")
plt.ylabel("Vcc (Volts)")
plt.xlabel("Time normalized (hours) ")

# Calculation of the actual ON time
np.array(WoobyDFVccStudy[WoobyDFVccStudy["vccVolts"]>5]["timeNorm"])[-1]/1000/60/60