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


#%% Reading of the files

#########################
######### Quad  #########
#########################

# All coeffs
folderName = "modelSimpleAllWeights_QuadSensor_PositionVariations"
folderName = "modelSimpleAllWeights_QuadSensor_PositionVariations_1_2_10"
folderName = "modelSimpleAllWeights_QuadSensor_Vader"
folderName = "modelSimpleAllWeights_QuadSensor_Vader_1order"
folderName = "modelSimpleAllWeights_QuadSensor_Vader_2order"

modelFolder = os.path.join(maindir, "models", folderName)

configFile =  os.path.join(modelFolder,"confModel.yaml")
modelPolyFeatAllCoeffsQuad, dfKPIAllCoeffsQuad, allDataTestAllCoeffsQuad, dfTotalQuad = train_and_test_wooby(modelFolder, configFile)
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


corr_matrix = allDataTestAllCoeffsQuad[["relativeVal_WU1", "relativeVal_WU2", "relativeVal_WU3",  "relativeVal_WU4"]].corr()

# %% Individual calculations

#########################
####  Quad Only 10k  ####
#########################

# All coeffs
folderName = "modelSimpleAllWeights_QuadSensor_PositionVariations_only_10k"
modelFolder = os.path.join(maindir, "models", folderName)

configFile =  os.path.join(modelFolder,"confModel.yaml")
modelPolyFeatAllCoeffsQuad10k, dfKPIAllCoeffsQuad10k, allDataTestAllCoeffsQuad10k, dfTotal10k = train_and_test_wooby(modelFolder, configFile)
print(dfKPIAllCoeffsQuad10k)

allDataTestAllCoeffsQuad10k[["relativeVal_WU1","relativeVal_WU2", "relativeVal_WU3", "relativeVal_WU4"]]
allDataTestAllCoeffsQuad10k["test"] = "Quad"
allDataTestAllCoeffsQuad10k["run"] = pd.Categorical(dfTotal10k["run"])

corr_matrix_10k = allDataTestAllCoeffsQuad[["relativeVal_WU1", "relativeVal_WU2", "relativeVal_WU3",  "relativeVal_WU4"]].corr()

#########################
####  Quad Only 500  ####
#########################

# All coeffs
folderName = "modelSimpleAllWeights_QuadSensor_PositionVariations_only_500"
modelFolder = os.path.join(maindir, "models", folderName)

configFile =  os.path.join(modelFolder,"confModel.yaml")
modelPolyFeatAllCoeffsQuad500, dfKPIAllCoeffsQuad500, allDataTestAllCoeffsQuad500, dfTotal500 = train_and_test_wooby(modelFolder, configFile)
print(dfKPIAllCoeffsQuad500)

allDataTestAllCoeffsQuad500[["relativeVal_WU1","relativeVal_WU2", "relativeVal_WU3", "relativeVal_WU4"]]
allDataTestAllCoeffsQuad500["test"] = "Quad"
allDataTestAllCoeffsQuad500["run"] = pd.Categorical(dfTotal500["run"])


corr_matrix_500 = allDataTestAllCoeffsQuad[["relativeVal_WU1", "relativeVal_WU2", "relativeVal_WU3",  "relativeVal_WU4"]].corr()

#########################
####  Quad 1-2-10    ####
#########################

# All coeffs
folderName = "modelSimpleAllWeights_QuadSensor_PositionVariations_1_2_10"
modelFolder = os.path.join(maindir, "models", folderName)

configFile =  os.path.join(modelFolder,"confModel.yaml")
modelPolyFeatAllCoeffsQuad1_2_10, dfKPIAllCoeffsQuad1_2_10, allDataTestAllCoeffsQuad1_2_10, dfTotal1_2_10 = train_and_test_wooby(modelFolder, configFile)
print(dfKPIAllCoeffsQuad1_2_10)

allDataTestAllCoeffsQuad1_2_10[["relativeVal_WU1","relativeVal_WU2", "relativeVal_WU3", "relativeVal_WU4"]]
allDataTestAllCoeffsQuad1_2_10["test"] = "Quad"
allDataTestAllCoeffsQuad1_2_10["run"] = pd.Categorical(dfTotal1_2_10["run"])


corr_matrix_1_2_10 = allDataTestAllCoeffsQuad[["relativeVal_WU1", "relativeVal_WU2", "relativeVal_WU3",  "relativeVal_WU4"]].corr()

#########################
####  Quad Vader     ####
#########################

# All coeffs
folderName = "modelSimpleAllWeights_QuadSensor_Vader"
modelFolder = os.path.join(maindir, "models", folderName)

configFile =  os.path.join(modelFolder,"confModel.yaml")
modelPolyFeatAllCoeffsQuadVader, dfKPIAllCoeffsQuadVader, allDataTestAllCoeffsQuadVader, dfTotalVader = train_and_test_wooby(modelFolder, configFile)
print(dfKPIAllCoeffsQuadVader)

allDataTestAllCoeffsQuadVader[["relativeVal_WU1","relativeVal_WU2", "relativeVal_WU3", "relativeVal_WU4"]]
allDataTestAllCoeffsQuadVader["test"] = "Quad"
allDataTestAllCoeffsQuadVader["run"] = pd.Categorical(dfTotalVader["run"])

coefsPipe = modelPolyFeatAllCoeffsQuadVader["LinearReg"].coef_
interceptPipe = modelPolyFeatAllCoeffsQuadVader["LinearReg"].intercept_
coefsNames = modelPolyFeatAllCoeffsQuadVader.steps[0][1].get_feature_names_out()
print(coefsNames)
print(coefsPipe)
print(interceptPipe)

corr_matrix_Vader = allDataTestAllCoeffsQuad[["relativeVal_WU1", "relativeVal_WU2", "relativeVal_WU3",  "relativeVal_WU4"]].corr()

################################
####  Quad Vader_1order     ####
################################

# All coeffs
folderName = "modelSimpleAllWeights_QuadSensor_Vader_1order"
modelFolder = os.path.join(maindir, "models", folderName)

configFile =  os.path.join(modelFolder,"confModel.yaml")
modelPolyFeatAllCoeffsQuadVader_1order, dfKPIAllCoeffsQuadVader_1order, allDataTestAllCoeffsQuadVader_1order, dfTotalVader_1order = train_and_test_wooby(modelFolder, configFile)
print(dfKPIAllCoeffsQuadVader_1order)

allDataTestAllCoeffsQuadVader_1order[["relativeVal_WU1","relativeVal_WU2", "relativeVal_WU3", "relativeVal_WU4"]]
allDataTestAllCoeffsQuadVader_1order["test"] = "Quad"
allDataTestAllCoeffsQuadVader_1order["run"] = pd.Categorical(dfTotalVader_1order["run"])

coefsPipe = modelPolyFeatAllCoeffsQuadVader_1order["LinearReg"].coef_
interceptPipe = modelPolyFeatAllCoeffsQuadVader_1order["LinearReg"].intercept_
coefsNames = modelPolyFeatAllCoeffsQuadVader_1order.steps[0][1].get_feature_names_out()
print(coefsNames)
print(coefsPipe)
print(interceptPipe)

corr_matrix_Vader_1order = allDataTestAllCoeffsQuad[["relativeVal_WU1", "relativeVal_WU2", "relativeVal_WU3",  "relativeVal_WU4"]].corr()


################################
####  Quad Vader_2order     ####
################################

# All coeffs
folderName = "modelSimpleAllWeights_QuadSensor_Vader_2order"
modelFolder = os.path.join(maindir, "models", folderName)

configFile =  os.path.join(modelFolder,"confModel.yaml")
modelPolyFeatAllCoeffsQuadVader_2order, dfKPIAllCoeffsQuadVader_2order, allDataTestAllCoeffsQuadVader_2order, dfTotalVader_2order = train_and_test_wooby(modelFolder, configFile)
print(dfKPIAllCoeffsQuadVader_2order)

allDataTestAllCoeffsQuadVader_2order[["relativeVal_WU1","relativeVal_WU2", "relativeVal_WU3", "relativeVal_WU4"]]
allDataTestAllCoeffsQuadVader_2order["test"] = "Quad"
allDataTestAllCoeffsQuadVader_2order["run"] = pd.Categorical(dfTotalVader_2order["run"])

coefsPipe = modelPolyFeatAllCoeffsQuadVader_2order["LinearReg"].coef_
interceptPipe = modelPolyFeatAllCoeffsQuadVader_2order["LinearReg"].intercept_
coefsNames = modelPolyFeatAllCoeffsQuadVader_2order.steps[0][1].get_feature_names_out()
print(coefsNames)
print(coefsPipe)
print(interceptPipe)

corr_matrix_Vader_2order = allDataTestAllCoeffsQuad[["relativeVal_WU1", "relativeVal_WU2", "relativeVal_WU3",  "relativeVal_WU4"]].corr()



#%% Supplement plots


f = plt.figure(figsize=(19, 15))
plt.matshow(corr_matrix, fignum=f.number)
plt.xticks(range(corr_matrix.shape[0]), list(corr_matrix.columns.values), fontsize=14, rotation=0)
plt.yticks(range(corr_matrix.shape[0]), list(corr_matrix.columns.values), fontsize=14, rotation=0)
cb = plt.colorbar()
cb.ax.tick_params(labelsize=14)


#with sns.color_palette("Spectral", as_cmap=True):

#sns.pairplot(data=allDataTestAllCoeffs[["realWeight", "relativeVal_WU1", "relativeVal_WU2", "relativeVal_WU3"]], hue="realWeight", palette="Spectral")

#sns.pairplot(data=allDataTestAllCoeffs[["absError", "relativeVal_WU1", "relativeVal_WU2", "relativeVal_WU3"]], hue="absError", palette="Spectral")

# Performance plots
sns.pairplot(data=allDataTestAllCoeffsQuad[["test", "realWeight", "relativeVal_WU1", "relativeVal_WU2", "relativeVal_WU3",  "relativeVal_WU4", "absError", "absErrorOK"]], hue="absErrorOK")

sns.pairplot(data=allDataTestAllCoeffsQuad[["run", "realWeight", "relativeVal_WU1", "relativeVal_WU2", "relativeVal_WU3",  "relativeVal_WU4", "absError"]], hue="run")



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
plt.xlabel("Real weight [gr]")
plt.ylabel("Relatives values [no units]")

# Coefficients 
plt.figure()
plt.bar(coefsNames, coefsPipe)

# %% 

meanVal10k = (allDataTestAllCoeffsQuad10k[allDataTestAllCoeffsQuad10k.run == 1].relativeVal_WU1.mean() + 
allDataTestAllCoeffsQuad10k[allDataTestAllCoeffsQuad10k.run == 1].relativeVal_WU2.mean() + 
allDataTestAllCoeffsQuad10k[allDataTestAllCoeffsQuad10k.run == 1].relativeVal_WU3.mean() + 
allDataTestAllCoeffsQuad10k[allDataTestAllCoeffsQuad10k.run == 1].relativeVal_WU4.mean() )/4

meanVal500 = (allDataTestAllCoeffsQuad500[allDataTestAllCoeffsQuad500.run == 1].relativeVal_WU1.mean() + 
allDataTestAllCoeffsQuad500[allDataTestAllCoeffsQuad500.run == 1].relativeVal_WU2.mean() + 
allDataTestAllCoeffsQuad500[allDataTestAllCoeffsQuad500.run == 1].relativeVal_WU3.mean() + 
allDataTestAllCoeffsQuad500[allDataTestAllCoeffsQuad500.run == 1].relativeVal_WU4.mean() )/4


#meanVal = allDataTestAllCoeffsQuad10k[allDataTestAllCoeffsQuad10k.run == 1].relativeVal_WU1.mean()
i
# Other plots
plt.figure()
plt.scatter(allDataTestAllCoeffsQuad10k[["run"]], (10410/10e3)*(allDataTestAllCoeffsQuad10k[["relativeVal_WU1"]]-meanVal10k)/meanVal10k, marker = "d", color="blue",   label="10kg relativeVal_WU1")
plt.scatter(allDataTestAllCoeffsQuad10k[["run"]], (10410/10e3)*(allDataTestAllCoeffsQuad10k[["relativeVal_WU2"]]-meanVal10k)/meanVal10k, marker = "d", color="orange", label="10kg relativeVal_WU2")
plt.scatter(allDataTestAllCoeffsQuad10k[["run"]], (10410/10e3)*(allDataTestAllCoeffsQuad10k[["relativeVal_WU3"]]-meanVal10k)/meanVal10k, marker = "d", color="green",  label="10kg relativeVal_WU3")
plt.scatter(allDataTestAllCoeffsQuad10k[["run"]], (10410/10e3)*(allDataTestAllCoeffsQuad10k[["relativeVal_WU4"]]-meanVal10k)/meanVal10k, marker = "d", color="red",    label="10kg relativeVal_WU4")
plt.scatter(allDataTestAllCoeffsQuad500[["run"]], (500/10e3)*(allDataTestAllCoeffsQuad500[["relativeVal_WU1"]]-meanVal500)/meanVal500, marker = "o", color="blue",   label="500g relativeVal_WU1")
plt.scatter(allDataTestAllCoeffsQuad500[["run"]], (500/10e3)*(allDataTestAllCoeffsQuad500[["relativeVal_WU2"]]-meanVal500)/meanVal500, marker = "o", color="orange", label="500g relativeVal_WU2")
plt.scatter(allDataTestAllCoeffsQuad500[["run"]], (500/10e3)*(allDataTestAllCoeffsQuad500[["relativeVal_WU3"]]-meanVal500)/meanVal500, marker = "o", color="green",  label="500g relativeVal_WU3")
plt.scatter(allDataTestAllCoeffsQuad500[["run"]], (500/10e3)*(allDataTestAllCoeffsQuad500[["relativeVal_WU4"]]-meanVal500)/meanVal500, marker = "o", color="red",    label="500g relativeVal_WU4")
plt.legend()
plt.grid(True)
plt.title("10 kg vs 5 gr comparison")



