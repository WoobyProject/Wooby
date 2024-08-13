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
from scipy.stats import norm
import re
import yaml

import seaborn as sns


from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.io as pio
pio.renderers.default='browser'



#%% Model selection

###################################
######### Spidey and Beetle  ######
###################################

modelForTest = "BeetleXPosition3"

match modelForTest:
    case "SpideyWood":
        datasetFolder = os.path.join(maindir, "datasets/WoobySpideyWood")           # Unknown use
    case "Spidey_v1":
        datasetFolder = os.path.join(maindir, "datasets/WoobyQuadHX711ForSpidey")   # Only used for the configuration evaluation
    case "Spidey_v2":
        datasetFolder = os.path.join(maindir, "datasets/WoobyQuadHX711ForSpidey2")
        folderName = "model_Spidey_v2"
    case "Beetlev1":
        datasetFolder = os.path.join(maindir, "datasets/WoobyQuadHX711ForBeattle")
        folderName = "model_Beetle_v1"
    case "BeetlePrerun":
        datasetFolder = os.path.join(maindir, "datasets/WoobyQuadHX711ForBeetleCalibration")
        folderName = "model_Beetle_calibration_prerun"
    case "BeetleFinalRun":
        datasetFolder = os.path.join(maindir, "datasets/WoobyQuadHX711ForBeetle2")
        folderName = "model_Beetle_calibration_final_run"
    case "BeetlePosition":
        datasetFolder = os.path.join(maindir, "datasets/WoobyQuadHX711ForBeetlePosition")
        folderName = "model_Beetle_position"
    case "BeetleInConfPosition":
        datasetFolder = os.path.join(maindir, "datasets/WoobyInConfBeetlePosition")
        folderName = "model_Beetle_inconfig_position"
    case "BeetleNew3Dpieces":
        datasetFolder = os.path.join(maindir, "datasets/WoobyQuadHX711ForBeetleNew3DPieces")
        folderName = "model_Beetle_new3Dpieces"
    case "BeetleXPosition1":
        datasetFolder = os.path.join(maindir, "datasets/WoobyQuadHX711ForX")
        folderName = "model_Beetle_X_Position1"
    case "BeetleXPosition2":
        datasetFolder = os.path.join(maindir, "datasets/WoobyQuadHX711ForX")
        folderName = "model_Beetle_X_Position2"
    case "BeetleXPosition3":
        datasetFolder = os.path.join(maindir, "datasets/WoobyQuadHX711ForX")
        folderName = "model_Beetle_X_Position3"


if folderName == "model_Beetle_inconfig_position":
    Wooby().convert_txt_to_csv(datasetFolder)

        
#%% Getting the weights from the folder

extension = "csv"
uniqueValuesWeights = createYMLfromFolder(datasetFolder, extension=extension)
print(uniqueValuesWeights)


#%% Reading of the files

configFile =  os.path.join(maindir, "models", folderName,"confModel.yaml")

"""
configFile = [ os.path.join(maindir, "models", "model_Beetle_calibration_prerun","confModel.yaml"), \
                os.path.join(maindir, "models", "model_Beetle_calibration_final_run","confModel.yaml")]
  
"""

modelPolyFeatAllCoeffsQuad, dfKPIAllCoeffsQuad, allDataTestAllCoeffsQuad, dfTotalQuad, allDfListForAllConfiFiles = train_and_test_wooby(configFile)
print(dfKPIAllCoeffsQuad)

allDataTestAllCoeffsQuad[["relativeVal_WU1","relativeVal_WU2", "relativeVal_WU3", "relativeVal_WU4"]]
allDataTestAllCoeffsQuad["test"] = "Quad"
allDataTestAllCoeffsQuad["run"] = pd.Categorical(dfTotalQuad["run"])
allDataTestAllCoeffsQuad["absErrorOK"] = abs(allDataTestAllCoeffsQuad["absError"])<5

coefsPipe = modelPolyFeatAllCoeffsQuad["LinearReg"].coef_
interceptPipe = modelPolyFeatAllCoeffsQuad["LinearReg"].intercept_
coefsNames = modelPolyFeatAllCoeffsQuad.steps[0][1].get_feature_names_out()

print(coefsNames)
for i in range(1, len(coefsNames)):
    print("Sensor {} ({}): {}".format(i, coefsNames[i], coefsPipe[i]))
    

print("Intercept: {}".format(interceptPipe))

print(dfKPIAllCoeffsQuad["MaxAE"])
print(dfKPIAllCoeffsQuad["StdAE"])
print(dfKPIAllCoeffsQuad["MeanAE"])

corr_matrix = allDataTestAllCoeffsQuad[["relativeVal_WU1", "relativeVal_WU2", "relativeVal_WU3",  "relativeVal_WU4"]].corr()

# Calculation extra variables
# Apply the function to each DataFrame in the list
# processed_dfs = [extraCalculationWoobyDf(df) for df in allDfListForAllConfiFiles]
# dfTotalQuad = pd.concat(processed_dfs, ignore_index=True)

#%% Sanity check for data


# Define the mapping of relativeVal_WU and tAfterMeasureNorm columns
mapping = {
    "relativeVal_WU1": "tAfterMeasure1Norm",
    "relativeVal_WU2": "tAfterMeasure2Norm",
    "relativeVal_WU3": "tAfterMeasure3Norm",
    "relativeVal_WU4": "tAfterMeasure4Norm",
}

# Create an empty DataFrame to hold the reshaped data
plot_data = pd.DataFrame()

# Iterate over the mapping and concatenate the results
for sensor, (relative_val, measure_time) in enumerate(mapping.items(), start=1):
    temp_df = dfTotalQuad[["realWeight", "run", relative_val, measure_time]].rename(
        columns={relative_val: "relativeVal_WU", measure_time: "tAfterMeasureNorm"}
    )
    temp_df['sensor'] = sensor
    plot_data = pd.concat([plot_data, temp_df])

# Combine columns to create a more descriptive legend
plot_data['legend'] = plot_data.apply(lambda row: f"Weight: {row['realWeight']}, Run: {row['run']}, Sensor: {row['sensor']}", axis=1)

# Plotting
fig = px.line(
    plot_data,
    x="tAfterMeasureNorm",
    y="relativeVal_WU",
    color="legend",
    title="Relative Values vs Normalized After Measure Times"
)

fig.update_layout(
    xaxis_title="Normalized After Measure Time",
    yaxis_title="Relative Value (WU)",
    legend_title="Legend"
)

fig.show()
#%% Supplement plots

# Correlation matrix
f = plt.figure(figsize=(19, 15))
plt.matshow(corr_matrix, fignum=f.number)
plt.xticks(range(corr_matrix.shape[0]), list(corr_matrix.columns.values), fontsize=14, rotation=0)
plt.yticks(range(corr_matrix.shape[0]), list(corr_matrix.columns.values), fontsize=14, rotation=0)
cb = plt.colorbar()
cb.ax.tick_params(labelsize=14)


# Initial data plots (by run) 
filteredDataTestAllCoeffsQuad =  allDataTestAllCoeffsQuad #[allDataTestAllCoeffsQuad["realWeight"]== 4001]
sns.pairplot(data=filteredDataTestAllCoeffsQuad[["run", "relativeVal_WU1", "relativeVal_WU2", "relativeVal_WU3",  "relativeVal_WU4"]], hue="run")


#with sns.color_palette("Spectral", as_cmap=True):

#sns.pairplot(data=allDataTestAllCoeffs[["realWeight", "relativeVal_WU1", "relativeVal_WU2", "relativeVal_WU3"]], hue="realWeight", palette="Spectral")

#sns.pairplot(data=allDataTestAllCoeffs[["absError", "relativeVal_WU1", "relativeVal_WU2", "relativeVal_WU3"]], hue="absError", palette="Spectral")

# Performance plots
sns.pairplot(data=allDataTestAllCoeffsQuad[["test", "realWeight", "relativeVal_WU1", "relativeVal_WU2", "relativeVal_WU3",  "relativeVal_WU4", "absError", "absErrorOK"]], hue="absErrorOK")


# Performance plots (by run) 
sns.pairplot(data=allDataTestAllCoeffsQuad[["run", "realWeight", "relativeVal_WU1", "relativeVal_WU2", "relativeVal_WU3",  "relativeVal_WU4", "absError"]], hue="run")





# Absolute error distribution
plt.figure()
data = allDataTestAllCoeffsQuad["absError"]
plt.hist(data, bins=round(np.sqrt(2*len(allDataTestAllCoeffsQuad))), density=True, alpha=0.5, color='orange', edgecolor='black')

# Calculate mean and standard deviation for Gaussian curve
mu, std = norm.fit(data)

# Plot Gaussian bell curve
xmin, xmax = plt.xlim()
x = np.linspace(xmin, xmax, 100)
p = norm.pdf(x, mu, std)
plt.plot(x, p, 'k', linewidth=2)

# Add labels and title
plt.xlabel('Absolute Error')
plt.ylabel('Density')
plt.title('Absolute error Gaussian distribution ($\mu={:.2f}$, $\sigma={:.2f}$)'.format(round(mu, 2), round(std, 2)))
plt.grid(True)



# One-to-one performance
plt.figure()
plt.scatter(allDataTestAllCoeffsQuad[["realWeight"]], allDataTestAllCoeffsQuad[["predictWeight"]])
plt.plot([0,11e3], [0, 11e3], 'r--')
plt.legend()
plt.grid(True)


# One-to-one performance (by run)
plt.figure()

# Get unique runs and assign a unique color to each one
unique_runs = allDataTestAllCoeffsQuad["run"].unique()
colors = plt.cm.get_cmap('tab10', len(unique_runs))  # Get a colormap with the same number of colors as unique runs

for i, run in enumerate(unique_runs):
    data_for_run = allDataTestAllCoeffsQuad[allDataTestAllCoeffsQuad["run"] == run]
    plt.scatter(data_for_run["realWeight"], data_for_run["predictWeight"], color=colors(i), label=f"Run {run}")

plt.plot([0, 11e3], [0, 11e3], 'r--')
plt.legend()
plt.grid(True)
plt.xlabel("Real Weight")
plt.ylabel("Predicted Weight")
plt.title("One-to-one Performance")

plt.show()


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


#%% Sandbox

################################
# Calculations
################################
allDataTestAllCoeffsQuad["sumRelativeValUnbiased_WU"] = (allDataTestAllCoeffsQuad["relativeVal_WU1"]) +  (allDataTestAllCoeffsQuad["relativeVal_WU2"]) + \
                                                        (allDataTestAllCoeffsQuad["relativeVal_WU3"]) +  (allDataTestAllCoeffsQuad["relativeVal_WU4"]) 
allDataTestAllCoeffsQuad["sumRelativeVal_WU"] = abs(allDataTestAllCoeffsQuad["relativeVal_WU1"]) +  abs(allDataTestAllCoeffsQuad["relativeVal_WU2"]) + \
                                                abs(allDataTestAllCoeffsQuad["relativeVal_WU3"]) +  abs(allDataTestAllCoeffsQuad["relativeVal_WU4"]) 
for i in range(1, 5):
    allDataTestAllCoeffsQuad["percetageVal_WU{}".format(i)] = abs(allDataTestAllCoeffsQuad["relativeVal_WU{}".format(i)])  /  allDataTestAllCoeffsQuad["sumRelativeVal_WU"] 
    allDataTestAllCoeffsQuad["contribution_gr{}".format(i)] =  allDataTestAllCoeffsQuad["percetageVal_WU{}".format(i)] *  allDataTestAllCoeffsQuad["realWeight"]
    allDataTestAllCoeffsQuad["contribution_percent{}".format(i)] =  allDataTestAllCoeffsQuad["percetageVal_WU{}".format(i)] *  allDataTestAllCoeffsQuad["realWeight"]
    allDataTestAllCoeffsQuad["realValue_WU{}".format(i)] = dfTotalQuad["realValue_WU{}".format(i)]
    allDataTestAllCoeffsQuad["offset{}".format(i)] = dfTotalQuad["offset{}".format(i)]
    
    
    
#%%

################################
# Intial plots
################################

filteredDf = allDataTestAllCoeffsQuad[allDataTestAllCoeffsQuad["realWeight"]== 4944]
filteredDf = allDataTestAllCoeffsQuad

sns.pairplot(data=filteredDf[["run", "relativeVal_WU1", "relativeVal_WU2", "relativeVal_WU3",  "relativeVal_WU4", "sumRelativeVal_WU"]], hue="run")

plt.figure()
plt.scatter(allDataTestAllCoeffsQuad["realWeight"], allDataTestAllCoeffsQuad["sumRelativeVal_WU"])
plt.plot([0,11e3], np.array([0, 11e3])*200, 'r--')
plt.legend()
plt.grid(True)


#%%

################################
# Plots for relative values (per weight)
################################

#filteredData =  allDataTestAllCoeffsQuad[allDataTestAllCoeffsQuad["run"]== 1]

# filteredData = allDataTestAllCoeffsQuad
filteredData =  allDataTestAllCoeffsQuad[ (allDataTestAllCoeffsQuad["run"] == 1) | (allDataTestAllCoeffsQuad["run"] == 5)]
# filteredData =  allDataTestAllCoeffsQuad[ (allDataTestAllCoeffsQuad["run"] == 4) ]


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
fig = px.line_polar(all_data, r='r', theta='theta', line_close=True, color='realWeight',  start_angle=-135, direction='counterclockwise',  title="Results for the variable "+variableToPlot, hover_data=['realWeight'])
fig.show()

#%%

################################
# Plots for relative values (per run)
################################
# 
filteredData =  allDataTestAllCoeffsQuad[allDataTestAllCoeffsQuad["realWeight"] == 500] 
# filteredData =  allDataTestAllCoeffsQuad[allDataTestAllCoeffsQuad["realWeight"] == 2590] 
# filteredData =  allDataTestAllCoeffsQuad[allDataTestAllCoeffsQuad["realWeight"] == 5020] 
# filteredData =  allDataTestAllCoeffsQuad[allDataTestAllCoeffsQuad["realWeight"] == 7427] 
# filteredData =  allDataTestAllCoeffsQuad[allDataTestAllCoeffsQuad["realWeight"] == 500]
# filteredData =  allDataTestAllCoeffsQuad[allDataTestAllCoeffsQuad["realWeight"] == 2980]
# filteredData =  allDataTestAllCoeffsQuad
filteredData = filteredData.reset_index()


variableToPlot = "relativeVal_WU"
# variableToPlot = "offset"
# variableToPlot = "realValue_WU"

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
fig = px.line_polar(all_data, r='r', theta='theta', line_close=True, color='run', start_angle=-135, direction='counterclockwise', title="Results for the variable "+variableToPlot, hover_data=['realWeight'])
fig.show()


#%% Sandbox sum

filteredData = allDataTestAllCoeffsQuad
filteredData =  allDataTestAllCoeffsQuad[allDataTestAllCoeffsQuad["run"] == 1]
# filteredData =  allDataTestAllCoeffsQuad


# Replicate each row four times
df_repeated = pd.concat([filteredData] * 4, ignore_index=True)

# Create 'sensor' column indicating which 'offset' column it came from
df_repeated['sensor'] = [1, 2, 3, 4] * len(filteredData)

# Combine 'offset' columns into a single column
offset_columns = ['offset1', 'offset2', 'offset3', 'offset4']
df_repeated['offset'] = df_repeated.apply(lambda row: row[offset_columns[row['sensor'] - 1]], axis=1)
offset_columns = ['relativeVal_WU1', 'relativeVal_WU2', 'relativeVal_WU3', 'relativeVal_WU4']
df_repeated['relativeVal_WU'] = df_repeated.apply(lambda row: row[offset_columns[row['sensor'] - 1]], axis=1)

df_repeated['realWeightPlot'] = df_repeated['realWeight'] + 30*df_repeated['sensor'] 
df_repeated['sensor'] = df_repeated['sensor'].astype('category') 

fig = px.scatter(df_repeated, x="realWeightPlot", y="offset", color="sensor",  hover_data=['realWeight'], error_y="relativeVal_WU", error_y_minus=0*df_repeated['offset'])
fig.update_layout(scattermode="group", scattergap=0.75)
fig.show()


# plt.figure
# plt.scatter(filteredData["realWeight"], filteredData["offset1"] )
# plt.scatter(filteredData["realWeight"], filteredData["realValue_WU1"])
# plt.grid()

#%% Sandbox sum

filteredData = allDataTestAllCoeffsQuad
filteredData = filteredData.reset_index()          

filteredData["sumRelativeValUnbiased_gr"] = filteredData["sumRelativeValUnbiased_WU"]/215.84
fig = px.scatter(filteredData, x="realWeight", y="sumRelativeValUnbiased_WU", color="run",  hover_data=['realWeight'])
fig.show()

fig = px.scatter(filteredData, x="realWeight", y="sumRelativeValUnbiased_gr", color="run",  hover_data=['realWeight'])
fig.show()


#%% Sandbox centroids


# For Beetle
kPosVectorX = np.array([-np.sqrt(2), np.sqrt(2),  np.sqrt(2), -np.sqrt(2)  ])
kPosVectorY = np.array([ np.sqrt(2), np.sqrt(2), -np.sqrt(2), -np.sqrt(2)  ])

# For Beetle Calibration
kPosVectorX = np.array([-np.sqrt(2), np.sqrt(2),  np.sqrt(2), -np.sqrt(2)  ])
kPosVectorY = np.array([-np.sqrt(2),-np.sqrt(2),  np.sqrt(2),  np.sqrt(2)  ])

allDataTestAllCoeffsQuad["centroid_x"]  = allDataTestAllCoeffsQuad["relativeVal_WU1"] * kPosVectorX[0] \
                                        + allDataTestAllCoeffsQuad["relativeVal_WU2"] * kPosVectorX[1] \
                                        + allDataTestAllCoeffsQuad["relativeVal_WU3"] * kPosVectorX[2] \
                                        + allDataTestAllCoeffsQuad["relativeVal_WU4"] * kPosVectorX[3] 
                
allDataTestAllCoeffsQuad["centroid_y"]  = allDataTestAllCoeffsQuad["relativeVal_WU1"] * kPosVectorY[0] \
                                        + allDataTestAllCoeffsQuad["relativeVal_WU2"] * kPosVectorY[1] \
                                        + allDataTestAllCoeffsQuad["relativeVal_WU3"] * kPosVectorY[2] \
                                        + allDataTestAllCoeffsQuad["relativeVal_WU4"] * kPosVectorY[3] 
                                    
                                                            
                
filteredData =  allDataTestAllCoeffsQuad[allDataTestAllCoeffsQuad["realWeight"] < 10e3] 
filteredData = filteredData.reset_index()

maxValuesDf = pd.DataFrame(columns=["centroid_x", "centroid_y", "sensor"] )

for ii in range(0,4):
    maskVector = np.zeros(4)
    maskVector[ii] = 1
    maxValue = max(allDataTestAllCoeffsQuad["relativeVal_WU{}".format(ii+1)])
    maxValuesDf.loc[ii, "centroid_x"] = np.dot( maxValue*maskVector, kPosVectorX)
    maxValuesDf.loc[ii, "centroid_y"] = np.dot( maxValue*maskVector, kPosVectorY)
    maxValuesDf.loc[ii, "sensor"] = 100+ii
                                            

fig = px.scatter(filteredData, x="centroid_x", y="centroid_y", color="run",  size='realWeight', hover_data=['realWeight'])
# fig.add_scatter(mode='markers', x=maxValuesDf["centroid_x"], y=maxValuesDf["centroid_y"])
fig.show()  

#%% Sandbox new way of calibration


filteredData =  allDataTestAllCoeffsQuad[allDataTestAllCoeffsQuad["run"] == 2]
filteredData = filteredData.reset_index()


fig = px.scatter(filteredData, x="realWeight", y="percetageVal_WU1", color="run",  hover_data=['realWeight'])
fig.add_scatter(mode='markers', x=filteredData["realWeight"], y=filteredData["percetageVal_WU2"])
fig.add_scatter(mode='markers', x=filteredData["realWeight"], y=filteredData["percetageVal_WU3"])
fig.add_scatter(mode='markers', x=filteredData["realWeight"], y=filteredData["percetageVal_WU4"])
fig.show()  


fig = px.scatter(filteredData, x="realWeight", y="contribution_gr1", color="run",  hover_data=['realWeight'])
fig.add_scatter(mode='markers', x=filteredData["realWeight"], y=filteredData["contribution_gr2"])
fig.add_scatter(mode='markers', x=filteredData["realWeight"], y=filteredData["contribution_gr3"])
fig.add_scatter(mode='markers', x=filteredData["realWeight"], y=filteredData["contribution_gr4"])
fig.show()  


fig = px.scatter(filteredData, x="realWeight", y="realValue_WU1", color="run",  hover_data=['realWeight'])
fig.add_scatter(mode='markers', x=filteredData["realWeight"], y=filteredData["realValue_WU2"])
fig.add_scatter(mode='markers', x=filteredData["realWeight"], y=filteredData["realValue_WU3"])
fig.add_scatter(mode='markers', x=filteredData["realWeight"], y=filteredData["realValue_WU4"])
fig.show()  


fig = px.scatter(filteredData, x="realWeight", y="relativeVal_WU1", color="run",  hover_data=['realWeight'])
fig.add_scatter(mode='markers', x=filteredData["realWeight"], y=filteredData["relativeVal_WU2"])
fig.add_scatter(mode='markers', x=filteredData["realWeight"], y=filteredData["relativeVal_WU3"])
fig.add_scatter(mode='markers', x=filteredData["realWeight"], y=filteredData["relativeVal_WU4"])
fig.show()  

#%% 

filteredData =  allDataTestAllCoeffsQuad[allDataTestAllCoeffsQuad["run"] == 1]
#filteredData =  allDataTestAllCoeffsQuad
filteredData = filteredData.reset_index()

dataTraining = {}
regs = [0, 0, 0, 0]

for i in range(1, 5):
    
  X = np.array(filteredData[["relativeVal_WU{}".format(i) ]]) #  relativeValue_WU
  # y = np.array(filteredData["realWeight"])
  y = np.array(filteredData[ "contribution_gr{}".format(i) ])
  
  # X = X.reshape((-1, 1))
  y = y.reshape((-1, 1))
  
  reg = LinearRegression().fit(X, y)
  regs[i-1] = reg
  
  # The coefficients & interception
  coeff = reg.coef_
  intercept = reg.intercept_
  
  dataTraining ["coeffsreg{}".format(i)] = coeff[0][0]
  dataTraining ["intercept{}".format(i)] = intercept[0]

  
calculatedWeight = 0*filteredData["realWeight"]

for i in range(1, 5):
    
    calculatedWeight = calculatedWeight + dataTraining["coeffsreg{}".format(i)] * (filteredData["relativeVal_WU{}".format(i)]) + dataTraining["intercept{}".format(i)] 
  
    
filteredData["newCalculatedWeight"] = calculatedWeight
  

# Plot for final regression real weight vs. calculated weight

fig = px.scatter(filteredData, x="realWeight", y="newCalculatedWeight", color="run",  hover_data=['realWeight'])
fig.show()  

# Plot for final regression real weight vs. calculated weight
filteredData["newAE"] = filteredData["newCalculatedWeight"] - filteredData["realWeight"]
fig = px.scatter(filteredData, x="realWeight", y="newAE", color="run",  hover_data=['realWeight'])
fig.show()  


print("Std Dev of A.E.: {:.2f} gr".format(np.std(filteredData["newCalculatedWeight"] - filteredData["realWeight"])))


# Plots for indidivual 
fig = px.scatter(filteredData, x="relativeVal_WU1", y="contribution_gr1", color="run",  hover_data=['realWeight'])
fig.add_scatter(mode='markers', x=filteredData["relativeVal_WU2"], y=filteredData["contribution_gr2"])
fig.add_scatter(mode='markers', x=filteredData["relativeVal_WU3"], y=filteredData["contribution_gr3"])
fig.add_scatter(mode='markers', x=filteredData["relativeVal_WU4"], y=filteredData["contribution_gr4"])


for i in range(0, 4):
    newX = np.linspace(0, 750e3, 100)
    newX = newX.reshape(1, -1)
    newY = regs[i].predict(newX.T)
    
    plotDf = pd.DataFrame({'x': newX[0],
                           'y': newY.T[0]})
    
    fig.add_scatter(x=plotDf["x"], y=plotDf["y"])



fig.show()


#%% Evaluation of calibrated value 

dfReportFinal = pd.DataFrame(columns=["realWeight","run"])
    
plt.figure()
for i in range(len(allDfListForAllConfiFiles)) :
    
    myDf = allDfListForAllConfiFiles[i]
    time = myDf["tBeforeMeasure1"] -  myDf["tBeforeMeasure1"].loc[0]
    # sumVals = myDf["relativeVal_WU1"] # + myDf["relativeVal_WU2"] +myDf["relativeVal_WU3"] + myDf["relativeVal_WU4"]
    sumVals = myDf["correctedValueFiltered"] # + myDf["relativeVal_WU2"] +myDf["relativeVal_WU3"] + myDf["relativeVal_WU4"]

    # print(np.round(np.mean(myDf["correctedValueFiltered"])))
    print(np.round((np.std(myDf["correctedValueFiltered"])),3))
    plt.plot(time, sumVals, label="{}".format(myDf["run"].loc[0]))
    
    dfReportFinal.loc[i, "realWeight"] = myDf["realWeight"].loc[0]
    dfReportFinal.loc[i, "run"] = myDf["run"].loc[0]
    dfReportFinal.loc[i, "std dev displayed value"] = np.std(myDf["correctedValueFiltered"])
    dfReportFinal.loc[i, "std dev error"] = np.std(myDf["correctedValueFiltered"] - myDf["realWeight"])
    
    
    
plt.grid(True)
plt.legend()
dfReportFinal
dfTotalQuad.groupby('realWeight')['correctedValueFiltered'].std()

#%% RUN WITH APPS


#%%

############# APP ###################
# Plots for relative values (per weight)
################################

app = Dash(__name__)

app.layout = html.Div([
    html.H4('Interactive scatter plot with Iris dataset'),
    dcc.Graph(id="scatter-plot"),
    html.P("Filter by petal width:"),
    dcc.RangeSlider(
        id='range-slider',
        min=1, max=3, step=1,
        marks={ 1: '1', 2: '2', 3: '3', },
        value=[1, 3]
    ),
])


@app.callback(
    Output("scatter-plot", "figure"), 
    Input("range-slider", "value"))

def update_bar_chart(slider_range):
    df = allDataTestAllCoeffsQuad # replace with your own data source
    
    # Filtering
    low, high = slider_range
    df["filteringVar"] = allDataTestAllCoeffsQuad['run'].cat.codes + 1
    mask = (df['filteringVar'] >= low) & (df['filteringVar'] <= high)
    filteredData = df[mask]
    filteredData = filteredData.reset_index()
    
    variableToPlot = "relativeVal_WU"
    #variableToPlot = "offset"
    #variableToPlot = "realValue_WU"

    print(filteredData[variableToPlot+"1"])
  
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
        
    return fig


app.run_server(debug=True)

#%%

############# APP ###################
# Plots for relative values (per run)
################################

app = Dash(__name__)

app.layout = html.Div([
    html.H4('Interactive scatter plot with Iris dataset'),
    dcc.Graph(id="scatter-plot"),
    html.P("Filter by petal width:"),
    dcc.RangeSlider(
        id='range-slider',
        min=0, max=10e3, step=500,
        value=[0, 10e3]
    ),
])


@app.callback(
    Output("scatter-plot", "figure"), 
    Input("range-slider", "value"))

def update_bar_chart(slider_range):
    df = allDataTestAllCoeffsQuad # replace with your own data source
    
    # Filtering
    low, high = slider_range
    df["filteringVar"] = allDataTestAllCoeffsQuad['realWeight']
    mask = (df['filteringVar'] >= low) & (df['filteringVar'] <= high)
    filteredData = df[mask]
    filteredData = filteredData.reset_index()
    
    variableToPlot = "relativeVal_WU"
    #variableToPlot = "offset"
    #variableToPlot = "realValue_WU"

    print(filteredData[variableToPlot+"1"])
  
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
    fig = px.line_polar(all_data, r='r', theta='theta', line_close=True, color='run', start_angle=135, title="Results for the variable "+variableToPlot, hover_data=['realWeight'])

    return fig


app.run_server(debug=True)

# Run this in Chrome: http://127.0.0.1:8050/


