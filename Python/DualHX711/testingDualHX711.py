#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  4 18:43:29 2021

@author: enriquem
"""


import sys
import os

maindir = maindir = "/Users/enriquem/Documents/HumanityLab/Wooby/GitHub2Test/Wooby/Python/"
print(maindir)
pckgdir = os.path.realpath(os.path.join(maindir, "pyWooby"))
sys.path.append(maindir)
print(pckgdir)

from pyWooby import Wooby
import matplotlib.pyplot as plt

#%% Creation of the Serial communication

myWooby = Wooby()

myWooby.availablePorts()

portWooby =  '/dev/tty.usbserial-0001' 
baudRateWooby = 115200;
    
myWooby.setupSerial(portWooby, baudRateWooby)

myWooby.tare()

#%% Reading of a calibration point

N_MAX_MEASURES = 15
SUBSET = "WoobyDualHX711" 
SOURCE = "SERIAL" # "TELNET" OR "SERIAL" 

REAL_WEIGHT = 1000      # in gr
SUFFIX = "MID_LEFT"

FILE_NAME = "{}_{}gr_{}.txt".format(SUBSET, REAL_WEIGHT, SUFFIX)
FILE_FOLDER = os.path.join("/Users/enriquem/Documents/HumanityLab/Wooby/GitHub2Test/Wooby/Python/datasets/", SUBSET)
                       
OVERWRITE = True

# 
# myWooby.tare()
dfDualLoadCell = myWooby.readNTimes("SERIAL", N_MAX_MEASURES)

# Export
myWooby.exportCSV(dfDualLoadCell, FILE_NAME, FILE_FOLDER, OVERWRITE)


#%% Plots for testing


fig, axs = plt.subplots(3,1)

plt.sca(axs[0])
# Plot of two sensors - normalized data !
plt.plot(dfDualLoadCell["tBeforeMeasure1"] ,  dfDualLoadCell["relativeVal_WU1"] , label="Sensor 1")
plt.plot(dfDualLoadCell["tBeforeMeasure2"] ,  dfDualLoadCell["relativeVal_WU2"] , label="Sensor 2")
plt.grid(True)
plt.legend()
plt.show()


plt.sca(axs[1])
# Plot of the sum of the two sensors
plt.plot(dfDualLoadCell["tBeforeMeasure1"] ,  dfDualLoadCell["relativeVal_WU1"] + dfDualLoadCell["relativeVal_WU2"] , label="Sum")
plt.grid(True)
plt.legend()
plt.show()



plt.sca(axs[2])
# Plot of the mult of the two sensors
plt.plot(dfDualLoadCell["tBeforeMeasure1"] ,  (dfDualLoadCell["realValue_WU1"] * dfDualLoadCell["realValue_WU2"]) , label="Skewness")
plt.grid(True)
plt.legend()
plt.show()



#%% Reading of the batch

fileNameList = ["WoobyDualHX711_1000gr_CENTER.txt",
                "WoobyDualHX711_1000gr_LEFT.txt",
                "WoobyDualHX711_1000gr_RIGHT.txt",
                "WoobyDualHX711_1000gr_MID_LEFT.txt",
                "WoobyDualHX711_1000gr_MID_RIGHT.txt",
                ]

allDfDualSensor = myWooby.importCSVbatch(fileNameList, FILE_FOLDER)

#%% Plotting of the batch

fig, axs = plt.subplots(3,1)

fig, axs2 = plt.subplots(2,1)

for ii, df in enumerate(allDfDualSensor):
    
    plt.sca(axs[0])
    # Plot of two sensors - normalized data !
    plt.plot(df["tBeforeMeasure1"]-df["tBeforeMeasure1"][0] ,  df["relativeVal_WU1"] , label="Sensor 1")
    plt.plot(df["tBeforeMeasure2"]-df["tBeforeMeasure2"][0] ,  df["relativeVal_WU2"] , label="Sensor 2")
    plt.grid(True)
    plt.legend()
    plt.show()
    
    
    plt.sca(axs[1])
    # Plot of the sum of the two sensors
    plt.plot(df["tBeforeMeasure1"]-df["tBeforeMeasure1"][0],  df["relativeVal_WU1"] + df["relativeVal_WU2"] , label="Sum")
    plt.grid(True)
    plt.legend()
    plt.show()
    
    
    
    plt.sca(axs[2])
    # Plot of the mult of the two sensors
    plt.plot(df["tBeforeMeasure1"]-df["tBeforeMeasure1"][0] ,  (df["realValue_WU1"] * df["realValue_WU2"]) , label="Skewness")
    plt.grid(True)
    plt.legend()
    plt.show()




    plt.sca(axs2[0])
    plt.scatter([fileNameList[ii]]*len(df),  (df["realValue_WU1"]) , label="Sensor1")
    plt.scatter([fileNameList[ii]]*len(df),  (df["realValue_WU2"]) , label="Sensor2")
    plt.grid(True)
    plt.legend()
    plt.show()

    