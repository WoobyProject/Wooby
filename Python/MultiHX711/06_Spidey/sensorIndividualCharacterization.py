#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 10 11:03:17 2024

@author: enriquem
"""
import sys
import os

"""
    For pyWoobypackage use
"""
maindir = "C:/Users/pasca/Wooby/devs/Python/"
maindir = "/Users/enriquem/Documents/HumanityLab/Wooby/GitHub3/Wooby/Python/"

pckgdir = os.path.realpath(os.path.join(maindir, "pyWooby"))
sys.path.append(maindir)
sys.path.append(pckgdir)
print(maindir)
print(pckgdir)


from pyWooby import Wooby
from pyWooby.calibration import *
from pyWooby.load import *


import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import re
import yaml
import seaborn as sns

#%% Initialization

## Initializing the Wooby element
myWooby = Wooby()


#%% Getting the weights from the folder

sensorDataFolder = os.path.join(maindir, "datasets/SensorCharacterization")

nSensors = 4
weights = np.array([0, 200, 500, 1000, 1200, 1500])
weights = np.array([0, 200, 500, 1000, 1500])

# weights = np.array([200])
dataForSensors = {}
allSensorsData = pd.DataFrame()

for iSensor in range(1, nSensors+1):
    folder_path = os.path.join(sensorDataFolder, str(iSensor))
    if os.path.isdir(folder_path):
        print("Reading sensor " + str(iSensor))
        sensorData = pd.DataFrame()
        for weight in weights:
            file_path = os.path.join(folder_path, "capture_{0}gr.txt".format(str(weight)))
            if os.path.isfile(file_path):
                print("\t Reading weight " + str(weight))
                dfWooby = myWooby.process_file(file_path)
                dfWooby["realWeight"] = weight
                sensorData = sensorData.append(dfWooby, ignore_index=True)
        
        sensorData["sensor"] = iSensor
        allSensorsData = allSensorsData.append(sensorData,ignore_index=True)
        dataForSensors[iSensor] = sensorData
        

# %% Initial plots

# Plotting the real value against the relative value to check the distribution
sns.scatterplot(data=allSensorsData, x="realWeight", y="relativeVal_WU1", hue="sensor", palette="Spectral")
plt.grid(True)

# Initial plots (by sensor)
sns.pairplot(data=allSensorsData[["sensor", "realWeight", "relativeVal_WU1"]], hue="sensor", palette="Spectral")

# %% Calibration

# Running a linear calibration for each sensor to get its coeff and intercept value
regForSensors = {}
data = {'Sensor': range(1, nSensors+1), 'Coeff': [0.0] * nSensors, 'Intercept': [0.0] * nSensors}
dfSensorCalib = pd.DataFrame(data)    

for iSensor in range(1, nSensors+1):
    regForSensors[iSensor] = myWooby.basicCalibration(dataForSensors[iSensor], verbose=False, xVar="relativeVal_WU1")
    dfSensorCalib.at[iSensor-1, 'Coeff']     = regForSensors[iSensor].coef_[0][0]
    dfSensorCalib.at[iSensor-1, 'Intercept'] = regForSensors[iSensor].intercept_
 
      
dfSensorCalib["InverseCoeff"] = 1/dfSensorCalib["Coeff"] ;

print(dfSensorCalib)

# %% Calibration evaluation

# Plotting of linear models for a sweep in the values of the WU inputs

plt.figure()
noUnitsRelativeValVector = np.linspace(np.min(allSensorsData["relativeVal_WU1"]), np.max(allSensorsData["relativeVal_WU1"]))
noUnitsRelativeValVector = np.reshape(noUnitsRelativeValVector, (len(noUnitsRelativeValVector), 1))

for iSensor in range(1, nSensors+1):
    
    dataRegSingleSensor = regForSensors[iSensor].predict(noUnitsRelativeValVector)
    plt.plot(noUnitsRelativeValVector, dataRegSingleSensor, label='Sensor {}'.format(iSensor))
    
plt.legend()
plt.grid()



# %% ############################################# 
#### EVALUATION OF SHIFTED WEIGHTS FOR SENSOR 2 ## 
####          TORSION EVALUATION STUDY          ## 
##################################################

iSensor = 2
sides = {"c", "l", "r"}
weightsShift = weights = np.array([500, 1000])

dataForSensorsShift = []
allSensorsDataShift = pd.DataFrame()

folder_path = os.path.join(sensorDataFolder, str(iSensor))
if os.path.isdir(folder_path):
    print("Reading sensor " + str(iSensor))
    sensorData = pd.DataFrame()
    for weight in weightsShift :
        for side in sides:
            file_path = os.path.join(folder_path, "capture_{0}gr_{1}.txt".format(str(weight), side))
            if os.path.isfile(file_path):
                print("\t Reading weight " + str(weight) + " with side " + side)
                dfWooby = myWooby.process_file(file_path)
                dfWooby["realWeight"] = weight
                dfWooby["side"] = side
                # sensorData = sensorData.append(dfWooby, ignore_index=True)
                sensorData  = dfWooby
                
                sensorData["sensor"] = iSensor
                allSensorsDataShift = allSensorsDataShift.append(sensorData,ignore_index=True)
                dataForSensorsShift.append(sensorData)
        
        
        
# %% Extra calculations

allSensorsDataShift["relativeVal_gr"] = allSensorsDataShift["relativeVal_WU1"] /213.788533
allSensorsDataShift["absError_gr"] = allSensorsDataShift["relativeVal_gr"] - allSensorsDataShift["realWeight"]
                
# %% 

plt.figure()
sns.scatterplot(data=allSensorsDataShift, x="realWeight", y="relativeVal_WU1", hue="side", palette="Spectral")
plt.grid(True)

plt.figure()
sns.scatterplot(data=allSensorsDataShift, x="realWeight", y="relativeVal_gr", hue="side", palette="Spectral")
plt.grid(True)

plt.figure()
sns.scatterplot(data=allSensorsDataShift, x="realWeight", y="absError_gr", hue="side", palette="Spectral")
plt.grid(True)

# Initial plots (by sensor)
sns.pairplot(data=allSensorsDataShift[["realWeight", "relativeVal_WU1", "side"]], hue="side", palette="Spectral")




