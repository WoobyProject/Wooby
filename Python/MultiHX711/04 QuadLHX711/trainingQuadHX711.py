#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 13 14:43:09 2023

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


datasetFolder = os.path.join(maindir, "datasets/WoobyQuadHX711ForTest")
uniqueValuesWeights = createYMLfromFolder(datasetFolder)
print(uniqueValuesWeights)


#%% Reading of the files

#########################
######### Quad  #########
#########################

# All coeffs
modelFolder = os.path.join(maindir, "models/modelSimpleAllWeights_QuadSensor")
# modelFolder = os.path.join(maindir, "models/modelSimpleAllWeights_QuadSensor_OnlyInteractions")


configFile =  os.path.join(modelFolder,"confModel.yaml")
modelPolyFeatAllCoeffsQuad, dfKPIAllCoeffsQuad, allDataTestAllCoeffsQuad = train_and_test_wooby(modelFolder, configFile)
print(dfKPIAllCoeffsQuad)

allDataTestAllCoeffsQuad[["relativeVal_WU1","relativeVal_WU2", "relativeVal_WU3", "relativeVal_WU4"]]
allDataTestAllCoeffsQuad["test"] = "Quad"

coefsPipe = modelPolyFeatAllCoeffsQuad["LinearReg"].coef_
interceptPipe = modelPolyFeatAllCoeffsQuad["LinearReg"].intercept_
print(modelPolyFeatAllCoeffsQuad.steps[0][1].get_feature_names_out())
print(coefsPipe)
print(interceptPipe)


corr_matrix = allDataTestAllCoeffsQuad[["relativeVal_WU1", "relativeVal_WU2", "relativeVal_WU3",  "relativeVal_WU4"]].corr()


#%% Supplement plots


f = plt.figure(figsize=(19, 15))
plt.matshow(corr_matrix, fignum=f.number)
plt.xticks(range(corr_matrix.shape[0]), list(corr_matrix.columns.values), fontsize=14, rotation=0)
plt.yticks(range(corr_matrix.shape[0]), list(corr_matrix.columns.values), fontsize=14, rotation=0)
cb = plt.colorbar()
cb.ax.tick_params(labelsize=14)


allDataTestAllCoeffsQuad["absErrorOK"] = abs(allDataTestAllCoeffsQuad["absError"])<7

#with sns.color_palette("Spectral", as_cmap=True):

#sns.pairplot(data=allDataTestAllCoeffs[["realWeight", "relativeVal_WU1", "relativeVal_WU2", "relativeVal_WU3"]], hue="realWeight", palette="Spectral")

#sns.pairplot(data=allDataTestAllCoeffs[["absError", "relativeVal_WU1", "relativeVal_WU2", "relativeVal_WU3"]], hue="absError", palette="Spectral")

# Performance plots
sns.pairplot(data=allDataTestAllCoeffsQuad[["test", "realWeight", "relativeVal_WU1", "relativeVal_WU2", "relativeVal_WU3",  "relativeVal_WU4", "absError", "absErrorOK"]], hue="absErrorOK")

sns.pairplot(data=allDataTestAllCoeffsQuad[["test", "realWeight", "relativeVal_WU1", "relativeVal_WU2", "relativeVal_WU3",  "relativeVal_WU4", "absError"]], hue="test")



plt.figure()
plt.scatter(allDataTestAllCoeffsQuad[["realWeight"]], allDataTestAllCoeffsQuad[["predictWeight"]])
plt.plot([0,11e3], [0, 11e3], 'r--')
plt.legend()
plt.grid(True)

# Other plots
plt.figure()
plt.scatter(allDataTestAllCoeffsQuad[["realWeight"]], allDataTestAllCoeffsQuad[["relativeVal_WU1"]], label="relativeVal_WU1")
plt.scatter(allDataTestAllCoeffsQuad[["realWeight"]], allDataTestAllCoeffsQuad[["relativeVal_WU2"]], label="relativeVal_WU2")
plt.scatter(allDataTestAllCoeffsQuad[["realWeight"]], allDataTestAllCoeffsQuad[["relativeVal_WU3"]], label="relativeVal_WU3")
plt.scatter(allDataTestAllCoeffsQuad[["realWeight"]], allDataTestAllCoeffsQuad[["relativeVal_WU4"]], label="relativeVal_WU4")
plt.legend()
plt.grid(True)

# Other plots
plt.figure()
plt.hist(allDataTestAllCoeffsQuad[["relativeVal_WU1"]], label="relativeVal_WU1")
plt.hist(allDataTestAllCoeffsQuad[["relativeVal_WU2"]], label="relativeVal_WU2")
plt.hist(allDataTestAllCoeffsQuad[["relativeVal_WU3"]], label="relativeVal_WU3")
plt.hist(allDataTestAllCoeffsQuad[["relativeVal_WU4"]], label="relativeVal_WU4")
plt.legend()
plt.grid(True)

#%%
allSensors = allDataTestAllCoeffsQuad["relativeVal_WU1"] + allDataTestAllCoeffsQuad["relativeVal_WU2"] + allDataTestAllCoeffsQuad["relativeVal_WU3"] + allDataTestAllCoeffsQuad["relativeVal_WU4"]
delta = allSensors/50*2 - allDataTestAllCoeffsQuad["realWeight"]                                                       

plt.figure()                                                            
plt.scatter(allDataTestAllCoeffsQuad[["realWeight"]], delta, label="delta")
plt.scatter(allDataTestAllCoeffsQuad[["realWeight"]], allDataTestAllCoeffsQuad[["absError"]], label="model")
plt.legend()
plt.grid(True)

#%% Sandbox


plt.figure()

allDataTestAllCoeffsQuad["relativeVal_WU1"].plot()

