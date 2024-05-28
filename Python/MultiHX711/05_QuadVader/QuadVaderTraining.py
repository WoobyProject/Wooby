#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  2 08:30:33 2023

@author: enriquem
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 30 18:10:00 2023

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



#%% Getting the weights from the folder

datasetFolder = os.path.join(maindir, "datasets/WoobyQuadHX711Vader")
#datasetFolder = os.path.join(maindir, "datasets/WoobyQuadHX711ForVader2")

uniqueValuesWeights = createYMLfromFolder(datasetFolder)
print(uniqueValuesWeights)

#%% Reading of the files

#########################
######### Vader 2  #########
#########################

# All coeffs
folderName = "modelSimpleAllWeights_QuadSensor_Vader_1order"

# folderName = "modelSimpleAllWeights_QuadSensor_Vader2"
# folderName = "modelSimpleAllWeights_QuadSensor_Vader2_2order"

modelFolder = os.path.join(maindir, "models", folderName)

configFile =  os.path.join(modelFolder,"confModel.yaml")
modelPolyFeatAllCoeffsQuad, dfKPIAllCoeffsQuad, allDataTestAllCoeffsQuad, dfTotalQuad = train_and_test_wooby(configFile)
print(dfKPIAllCoeffsQuad)

allDataTestAllCoeffsQuad[["relativeVal_WU1","relativeVal_WU2", "relativeVal_WU3", "relativeVal_WU4"]]
allDataTestAllCoeffsQuad["test"] = "Quad"
allDataTestAllCoeffsQuad["run"] = pd.Categorical(dfTotalQuad["run"])
allDataTestAllCoeffsQuad["absErrorOK"] = abs(allDataTestAllCoeffsQuad["absError"])<7

coefsPipe = modelPolyFeatAllCoeffsQuad["LinearReg"].coef_
interceptPipe = modelPolyFeatAllCoeffsQuad["LinearReg"].intercept_
coefsNames = modelPolyFeatAllCoeffsQuad.steps[0][1].get_feature_names_out()

print(coefsNames)
print(coefsPipe)
print(interceptPipe)

print(dfKPIAllCoeffsQuad["MaxAE"])
print(dfKPIAllCoeffsQuad["StdAE"])
print(dfKPIAllCoeffsQuad["MeanAE"])

corr_matrix = allDataTestAllCoeffsQuad[["relativeVal_WU1", "relativeVal_WU2", "relativeVal_WU3",  "relativeVal_WU4"]].corr()



#%% Supplement plots

# Correlation matrix
f = plt.figure(figsize=(19, 15))
plt.matshow(corr_matrix, fignum=f.number)
plt.xticks(range(corr_matrix.shape[0]), list(corr_matrix.columns.values), fontsize=14, rotation=0)
plt.yticks(range(corr_matrix.shape[0]), list(corr_matrix.columns.values), fontsize=14, rotation=0)
cb = plt.colorbar()
cb.ax.tick_params(labelsize=14)


# Initial data plots (by run) 
filteredDataTestAllCoeffsQuad =  allDataTestAllCoeffsQuad[allDataTestAllCoeffsQuad["realWeight"]== 4001]
sns.pairplot(data=filteredDataTestAllCoeffsQuad[["run", "relativeVal_WU1", "relativeVal_WU2", "relativeVal_WU3",  "relativeVal_WU4"]], hue="run")



#with sns.color_palette("Spectral", as_cmap=True):

#sns.pairplot(data=allDataTestAllCoeffs[["realWeight", "relativeVal_WU1", "relativeVal_WU2", "relativeVal_WU3"]], hue="realWeight", palette="Spectral")

#sns.pairplot(data=allDataTestAllCoeffs[["absError", "relativeVal_WU1", "relativeVal_WU2", "relativeVal_WU3"]], hue="absError", palette="Spectral")

# Performance plots
sns.pairplot(data=allDataTestAllCoeffsQuad[["test", "realWeight", "relativeVal_WU1", "relativeVal_WU2", "relativeVal_WU3",  "relativeVal_WU4", "absError", "absErrorOK"]], hue="absErrorOK")

# Performance plots (by run) 
sns.pairplot(data=allDataTestAllCoeffsQuad[["run", "realWeight", "relativeVal_WU1", "relativeVal_WU2", "relativeVal_WU3",  "relativeVal_WU4", "absError"]], hue="run")


# One-to-one performance
plt.figure()
plt.scatter(allDataTestAllCoeffsQuad[["realWeight"]], allDataTestAllCoeffsQuad[["predictWeight"]])
plt.plot([0,11e3], [0, 11e3], 'r--')
plt.legend()
plt.grid(True)

# Absolute error performance
plt.figure()
groups = allDataTestAllCoeffsQuad.groupby('run')
for name, group in groups:
    plt.plot(group.realWeight, group.absError, marker='o', linestyle='', markersize=5, label=name)

plt.legend(title="Run")
#plt.scatter(allDataTestAllCoeffsQuad[["realWeight"]], allDataTestAllCoeffsQuad[["absError"]], c=allDataTestAllCoeffsQuad["run"])
plt.plot([0,11e3], [  5,   5], 'r--')
plt.plot([0,11e3], [ -5,  -5], 'r--')
plt.plot([0,11e3], [ 10,  10], 'r--', alpha=0.2)
plt.plot([0,11e3], [-10, -10], 'r--', alpha=0.2)
plt.xlabel("Real weight [gr]")
plt.ylabel("Absolute error for model [gr]")
plt.grid(True)

# Other plots
plt.figure()
plt.scatter(allDataTestAllCoeffsQuad[["realWeight"]], allDataTestAllCoeffsQuad[["relativeVal_WU1"]], label="relativeVal_WU1")
plt.scatter(allDataTestAllCoeffsQuad[["realWeight"]], allDataTestAllCoeffsQuad[["relativeVal_WU2"]], label="relativeVal_WU2")
plt.scatter(allDataTestAllCoeffsQuad[["realWeight"]], allDataTestAllCoeffsQuad[["relativeVal_WU3"]], label="relativeVal_WU3")
plt.scatter(allDataTestAllCoeffsQuad[["realWeight"]], allDataTestAllCoeffsQuad[["relativeVal_WU4"]], label="relativeVal_WU4")
plt.legend()
plt.grid(True)
plt.xlabel("Real weight [gr]")
plt.ylabel("Relatives values [no units]")

# Coefficients 
plt.figure()
plt.bar(coefsNames, coefsPipe)

# %% Balance plots

import plotly.express as px
import plotly.io as pio
pio.renderers.default='browser'

# %%
################################
# Calculations
################################
allDataTestAllCoeffsQuad["sumRelativeVal_WU"] = abs(allDataTestAllCoeffsQuad["relativeVal_WU1"]) +  abs(allDataTestAllCoeffsQuad["relativeVal_WU2"]) + \
                                                abs(allDataTestAllCoeffsQuad["relativeVal_WU3"]) +  abs(allDataTestAllCoeffsQuad["relativeVal_WU4"]) 
for i in range(1, 5):
    allDataTestAllCoeffsQuad["percetageVal_WU{}".format(i)] = allDataTestAllCoeffsQuad["relativeVal_WU{}".format(i)]/allDataTestAllCoeffsQuad["sumRelativeVal_WU"] 
    allDataTestAllCoeffsQuad["realValue_WU{}".format(i)] = dfTotalQuad["realValue_WU{}".format(i)]
    allDataTestAllCoeffsQuad["offset{}".format(i)] = dfTotalQuad["offset{}".format(i)]
    
    
#%%

################################
# Plots for relative values (per weight)
################################

#filteredData =  allDataTestAllCoeffsQuad[allDataTestAllCoeffsQuad["run"]== 1]

filteredData = allDataTestAllCoeffsQuad
filteredData =  allDataTestAllCoeffsQuad[allDataTestAllCoeffsQuad["realWeight"] < 2000] # For Vader 1


filteredData = filteredData.reset_index()


variableToPlot = "relativeVal_WU"
variableToPlot = "offset"
variableToPlot = "realValue_WU"

# Create a list to store individual DataFrames
data_frames = []

# Iterate over the range
for i in range(len(filteredData)):
    data = {
        'r': [
            filteredData[variableToPlot+"1"][i],
            filteredData[variableToPlot+"2"][i],
            filteredData[variableToPlot+"3"][i],
            filteredData[variableToPlot+"4"][i]
        ],
        'theta': ['Sensor 1', 'Sensor 2', 'Sensor 3', 'Sensor 4'],
        'run': filteredData["run"][i],  # Add the 'run' variable
        'realWeight': filteredData["realWeight"][i]   # Add the 'realWeight' variable
    }
    data_frames.append(pd.DataFrame(data))

# Concatenate all DataFrames into a single DataFrame
all_data = pd.concat(data_frames, ignore_index=True)

# Plot all the data on the same figure with color coded by 'run'
fig = px.line_polar(all_data, r='r', theta='theta', line_close=True, color='realWeight', start_angle=-45, title="Results for the variable "+variableToPlot, hover_data=['realWeight'])
fig.show()

#%%
################################
# Plots for relative values (per run)
################################

filteredData =  allDataTestAllCoeffsQuad[allDataTestAllCoeffsQuad["realWeight"] == 4001] # For Vader 2
filteredData =  allDataTestAllCoeffsQuad[allDataTestAllCoeffsQuad["realWeight"] == 500] # For Vader 1: 7432 2481 500
filteredData =  allDataTestAllCoeffsQuad
filteredData = filteredData.reset_index()


variableToPlot = "relativeVal_WU"
#variableToPlot = "offset"
#variableToPlot = "realValue_WU"

# Create a list to store individual DataFrames
data_frames = []

# Iterate over the range
for i in range(len(filteredData)):
    data = {
        'r': [
            filteredData[variableToPlot+"1"][i],
            filteredData[variableToPlot+"2"][i],
            filteredData[variableToPlot+"3"][i],
            filteredData[variableToPlot+"4"][i]
        ],
        'theta': ['Sensor 1', 'Sensor 2', 'Sensor 3', 'Sensor 4'],
        'run': filteredData["run"][i],  # Add the 'run' variable
        'realWeight': filteredData["realWeight"][i]   # Add the 'realWeight' variable
    }
    data_frames.append(pd.DataFrame(data))

# Concatenate all DataFrames into a single DataFrame
all_data = pd.concat(data_frames, ignore_index=True)

# Plot all the data on the same figure with color coded by 'run'
fig = px.line_polar(all_data, r='r', theta='theta', line_close=True, color='run', start_angle=-45, title="Results for the variable "+variableToPlot, hover_data=['realWeight'])
fig.show()


#%% Sandbox centroids



filteredData =  allDataTestAllCoeffsQuad[allDataTestAllCoeffsQuad["realWeight"] < 10e3] # For Vader 1: 7432 2481 500


allDataTestAllCoeffsQuad["centroid_x"]  = allDataTestAllCoeffsQuad["relativeVal_WU1"] *  np.sqrt(2) \
                                        + allDataTestAllCoeffsQuad["relativeVal_WU2"] * -np.sqrt(2) \
                                        + allDataTestAllCoeffsQuad["relativeVal_WU3"] * -np.sqrt(2) \
                                        + allDataTestAllCoeffsQuad["relativeVal_WU4"] *  np.sqrt(2) \
                
allDataTestAllCoeffsQuad["centroid_y"]  = allDataTestAllCoeffsQuad["relativeVal_WU1"] * -np.sqrt(2) \
                                        + allDataTestAllCoeffsQuad["relativeVal_WU2"] * -np.sqrt(2) \
                                        + allDataTestAllCoeffsQuad["relativeVal_WU3"] * +np.sqrt(2) \
                                        + allDataTestAllCoeffsQuad["relativeVal_WU4"] * +np.sqrt(2) \
                                                            
                
                

fig = px.scatter(filteredData, x="centroid_x", y="centroid_y", color="run",  size='realWeight', hover_data=['realWeight'])
fig.show()  

                
                
                
                
