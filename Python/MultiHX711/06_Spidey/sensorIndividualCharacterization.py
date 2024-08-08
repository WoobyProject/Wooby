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
# Run on console for Spyder: %matplotlib qt
import pandas as pd
import numpy as np
import re
import yaml
import seaborn as sns

import glob

#%% Initialization

## Initializing the Wooby element
myWooby = Wooby()

def charge_file(folder_path, starting_string):
    file_paths = glob.glob(f"{folder_path}/{starting_string}*")
    return file_paths[0] if file_paths else ""


#%% Getting the weights from the folder

# Sensor charact # 1
listSensors = list(range(1, 5))
sensorDataFolder = os.path.join(maindir, "datasets/SensorCharacterization")
weights = np.array([0, 200, 500, 1000, 1200, 1500])
matchSensorNumber = False

# Sensor charact # 2
listSensors = [1, 2, 3, 4]
sensorDataFolder = os.path.join(maindir, "datasets/SensorCharacterizationBatch2")
weights = np.array([500, 1510])
matchSensorNumber = True


# Calculating the total of sensors
nSensors = len(listSensors)

# weights = np.array([200])
dataForSensors = {}
allSensorsData = pd.DataFrame()

for iSensor in listSensors:
    folder_path = os.path.join(sensorDataFolder, str(iSensor))
    if os.path.isdir(folder_path):
        print("Reading sensor " + str(iSensor))
        sensorData = pd.DataFrame()
        for weight in weights:
            file_name        = "capture_{0}gr.txt".format(str(weight))
            file_name_approx = "capture_{0}gr".format(str(weight))
            file_path = charge_file(folder_path, file_name_approx)
            if os.path.isfile(file_path):
                print("\t Reading weight " + str(weight))
                dfWooby = myWooby.process_file(file_path)
                dfWooby["realWeight"] = weight
                if matchSensorNumber:
                    dfWooby["relativeVal_WUFinal"] = dfWooby["relativeVal_WU{}".format(iSensor)]
                    dfWooby["offset_Final"] = dfWooby["offset{}".format(iSensor)]
                else:
                    dfWooby["relativeVal_WUFinal"] = dfWooby["relativeVal_WU1"] 
                    dfWooby["offset_Final"] = dfWooby["offset_1"] 
                sensorData = pd.concat([sensorData, dfWooby], ignore_index=True)
            else:
                print("\t File not found: '" + file_name + "'")
        
        sensorData["sensor"] = iSensor
        allSensorsData = pd.concat([allSensorsData, sensorData],ignore_index=True)
        dataForSensors[iSensor] = sensorData
        

# %% Initial plots

# Plotting the real value against the relative value to check the distribution
sns.scatterplot(data=allSensorsData, x="realWeight", y="relativeVal_WUFinal", hue="sensor", palette="tab10")
plt.grid(True)

# %% Sanitz check for sensors numbering and relativeValue numbering

sensorList = [1, 2, 3]
recordList = [2, 4, 1]

sensorList = [3, 3, 3, 3]
recordList = [1, 2, 3, 4]

sensorList = [2, 2, 2, 2]
recordList = [1, 2, 3, 4]

#sensorList = [1, 1, 1, 1]
#recordList = [1, 2, 3, 4]

#sensorList = [4, 4, 4, 4]
#recordList = [1, 2, 3, 4]

for (iS, iR) in zip(sensorList, recordList):
    print(iS)
    print(iR)
    plt.figure()
    filteredDataFrame = allSensorsData[allSensorsData['sensor'] == iS]
    sns.scatterplot(data=filteredDataFrame, x="realWeight", y="relativeVal_WU{}".format(iR), palette="tab10")
    plt.grid(True)

# %% Initial plots

filteredDataFrame = allSensorsData[allSensorsData['sensor'] == 1]
filteredDataFrame = allSensorsData

# Initial plots (by sensor)
sns.pairplot(data=filteredDataFrame[["sensor", "realWeight", "relativeVal_WU1", "relativeVal_WU2", "relativeVal_WU3", "relativeVal_WU4"]], hue="sensor", palette="tab10")


# Check for offset

sns.scatterplot(data = allSensorsData, x="realWeight", y="offset_Final", hue="sensor", palette="tab10") 

# %% Calibration

# Running a linear calibration for each sensor to get its coeff and intercept value
regForSensors = {}
data = {'Sensor': listSensors, 'Coeff': [0.0] * nSensors, 'Intercept': [0.0] * nSensors}
dfSensorCalib = pd.DataFrame(data)    

for it, iSensor in enumerate(listSensors, start=0):
    regForSensors[it] = myWooby.basicCalibration(dataForSensors[iSensor], verbose=False, xVar="relativeVal_WUFinal")
    dfSensorCalib.at[it, 'Coeff']     = regForSensors[it].coef_[0][0]
    dfSensorCalib.at[it, 'Intercept'] = regForSensors[it].intercept_
 
      
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




