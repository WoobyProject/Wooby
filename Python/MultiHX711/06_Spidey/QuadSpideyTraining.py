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

# datasetFolder = os.path.join(maindir, "datasets/WoobySpideyWood")
datasetFolder = os.path.join(maindir, "datasets/WoobyQuadHX711ForSpidey")
datasetFolder = os.path.join(maindir, "datasets/WoobyQuadHX711ForSpidey2")

uniqueValuesWeights = createYMLfromFolder(datasetFolder)
print(uniqueValuesWeights)

#%% Reading of the files

#########################
######### Spidey   ######
#########################

# Folder for the model to run
folderName = "model_Spidey_v2"

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
