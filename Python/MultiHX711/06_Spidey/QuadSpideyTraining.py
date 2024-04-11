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


from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.io as pio
pio.renderers.default='browser'


#%% Getting the weights from the folder

# datasetFolder = os.path.join(maindir, "datasets/WoobySpideyWood")
datasetFolder = os.path.join(maindir, "datasets/WoobyQuadHX711ForSpidey")   # Only used for the configuration evaluation
datasetFolder = os.path.join(maindir, "datasets/WoobyQuadHX711ForSpidey2")
# datasetFolder = os.path.join(maindir, "datasets/WoobyQuadHX711ForBeattle")

uniqueValuesWeights = createYMLfromFolder(datasetFolder)
print(uniqueValuesWeights)

#%% Reading of the files

#########################
######### Spidey   ######
#########################

# Folder for the model to run
folderName = "model_Spidey_v2"
# folderName = "model_Beetle_v1"

modelFolder = os.path.join(maindir, "models", folderName)

configFile =  os.path.join(modelFolder,"confModel.yaml")
modelPolyFeatAllCoeffsQuad, dfKPIAllCoeffsQuad, allDataTestAllCoeffsQuad, dfTotalQuad = train_and_test_wooby(modelFolder, configFile)
print(dfKPIAllCoeffsQuad)

allDataTestAllCoeffsQuad[["relativeVal_WU1","relativeVal_WU2", "relativeVal_WU3", "relativeVal_WU4"]]
allDataTestAllCoeffsQuad["test"] = "Quad"
allDataTestAllCoeffsQuad["run"] = pd.Categorical(dfTotalQuad["run"])
allDataTestAllCoeffsQuad["absErrorOK"] = abs(allDataTestAllCoeffsQuad["absError"])<5

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
filteredDataTestAllCoeffsQuad =  allDataTestAllCoeffsQuad #[allDataTestAllCoeffsQuad["realWeight"]== 4001]
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


#%% Sandbox

################################
# Calculations
################################
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



#%%

################################
# Plots for relative values (per weight)
################################

#filteredData =  allDataTestAllCoeffsQuad[allDataTestAllCoeffsQuad["run"]== 1]

filteredData = allDataTestAllCoeffsQuad
filteredData =  allDataTestAllCoeffsQuad[allDataTestAllCoeffsQuad["run"] == 2]


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
fig = px.line_polar(all_data, r='r', theta='theta', line_close=True, color='realWeight', start_angle=-45, title="Results for the variable "+variableToPlot, hover_data=['realWeight'])
fig.show()

#%%

################################
# Plots for relative values (per run)
################################

filteredData =  allDataTestAllCoeffsQuad[allDataTestAllCoeffsQuad["realWeight"] == 4001] 
filteredData =  allDataTestAllCoeffsQuad[allDataTestAllCoeffsQuad["realWeight"] == 0]
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
fig = px.line_polar(all_data, r='r', theta='theta', line_close=True, color='run', start_angle=135, title="Results for the variable "+variableToPlot, hover_data=['realWeight'])
fig.show()


#%% Sandbox centroids



filteredData =  allDataTestAllCoeffsQuad[allDataTestAllCoeffsQuad["realWeight"] < 3.1e3] 
filteredData = filteredData.reset_index()


allDataTestAllCoeffsQuad["centroid_x"]  = allDataTestAllCoeffsQuad["relativeVal_WU1"] * -np.sqrt(2) \
                                        + allDataTestAllCoeffsQuad["relativeVal_WU2"] *  np.sqrt(2) \
                                        + allDataTestAllCoeffsQuad["relativeVal_WU3"] *  np.sqrt(2) \
                                        + allDataTestAllCoeffsQuad["relativeVal_WU4"] * -np.sqrt(2) \
                
allDataTestAllCoeffsQuad["centroid_y"]  = allDataTestAllCoeffsQuad["relativeVal_WU1"] *  np.sqrt(2) \
                                        + allDataTestAllCoeffsQuad["relativeVal_WU2"] *  np.sqrt(2) \
                                        + allDataTestAllCoeffsQuad["relativeVal_WU3"] * -np.sqrt(2) \
                                        + allDataTestAllCoeffsQuad["relativeVal_WU4"] * -np.sqrt(2) \
                                                            
                
                

fig = px.scatter(filteredData, x="centroid_x", y="centroid_y", color="run",  size='realWeight', hover_data=['realWeight'])
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


