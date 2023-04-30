#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  4 18:43:29 2021

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


datasetFolder = "../datasets/WoobyTripleHX711ForTest3"
uniqueValuesWeights = createYMLfromFolder(datasetFolder)
print(uniqueValuesWeights)

datasetFolder = "../datasets/WoobyTripleHX711ForTest2"
uniqueValuesWeights = createYMLfromFolder(datasetFolder)
print(uniqueValuesWeights)

#%% Reading of the files

#########################
######### Wood  #########
#########################

# All coeffs
modelFolder = "../models/modelSimpleAllWeights_Wood"
configFile = os.path.join(modelFolder,"confModel.yaml")
modelPolyFeatAllCoeffsWoood, dfKPIAllCoeffsWoood, allDataTestAllCoeffsWoood = train_and_test_wooby(modelFolder, configFile)
print(dfKPIAllCoeffsWoood)

allDataTestAllCoeffsWoood[["relativeVal_WU1","relativeVal_WU2", "relativeVal_WU3"]]
allDataTestAllCoeffsWoood["test"] = "wood"

# Only Interactions
modelFolder = "../models/modelSimpleAllWeights_Wood_OnlyInteractions"
configFile = os.path.join(modelFolder,"confModel.yaml")
modelPolyFeatOnlyInterWoood, dfKPIOnlyInterWoood, allDataTestOnlyInterWoood = train_and_test_wooby(modelFolder, configFile)
print(dfKPIOnlyInterWoood)

###########################
######### Eraser  #########
###########################

# All coeffs
modelFolder = "../models/modelSimpleAllWeights_Eraser"
configFile = os.path.join(modelFolder,"confModel.yaml")
modelPolyFeatAllCoeffs, dfKPIAllCoeffs, allDataTestAllCoeffs = train_and_test_wooby(modelFolder, configFile)
print(dfKPIAllCoeffs)

allDataTestAllCoeffs["test"] = "eraser"

# Only interactions
modelFolder = "../models/modelSimpleAllWeights_Eraser_OnlyInteractions"
configFile = os.path.join(modelFolder,"confModel.yaml")
modelPolyFeatOnlyInter, dfKPIOnlyInter, allDataTestOnlyInter = train_and_test_wooby(modelFolder, configFile)
print(dfKPIOnlyInter)

###############################
######### Comparison  #########
###############################


df_AllModels = pd.concat([dfKPIAllCoeffsWoood, dfKPIOnlyInterWoood, 
                          dfKPIAllCoeffs, dfKPIOnlyInter], ignore_index=True)

df_AllData =  pd.concat([allDataTestAllCoeffsWoood, allDataTestAllCoeffs], ignore_index=True)

print("")
print(df_AllModels.drop("name", axis=1))


#%% Supplement plots

allDataTestAllCoeffs["absErrorOK"] = abs(allDataTestAllCoeffs["absError"] )<50

#with sns.color_palette("Spectral", as_cmap=True):

#sns.pairplot(data=allDataTestAllCoeffs[["realWeight", "relativeVal_WU1", "relativeVal_WU2", "relativeVal_WU3"]], hue="realWeight", palette="Spectral")

#sns.pairplot(data=allDataTestAllCoeffs[["absError", "relativeVal_WU1", "relativeVal_WU2", "relativeVal_WU3"]], hue="absError", palette="Spectral")

sns.pairplot(data=df_AllData[["test", "realWeight", "relativeVal_WU1", "relativeVal_WU2", "relativeVal_WU3"]], hue="test", palette="Spectral")










#%%#############################
######### Sandbox  #############
################################


df = allDataTestAllCoeffs


ax = plot_test(allDataTestAllCoeffsWoood,"realWeight","relativeVal_WU1", color_="blue")
plot_test(allDataTestAllCoeffs, "realWeight","relativeVal_WU1", ax = ax, color_="red")




sCheckDfWood = sanityCheck(allDataTestAllCoeffsWoood)
sCheckDfWood["test"] = "wood"

sCheckDfEraser = sanityCheck(allDataTestAllCoeffs)
sCheckDfEraser["test"] = "eraser"


"""
ax1 = plot_test(sCheckDfWood,"realWeight","relValWU1_norm_mean", color_="blue")
plot_test(sCheckDfWood,     "realWeight","relValWU2_norm_mean", color_="blue", ax=ax1)
plot_test(sCheckDfWood,     "realWeight","relValWU3_norm_mean", color_="blue", ax=ax1)

plot_test(sCheckDfEraser, "realWeight","relValWU1_norm_mean", color_="red", ax=ax1)
plot_test(sCheckDfEraser, "realWeight","relValWU2_norm_mean", color_="red", ax=ax1)
plot_test(sCheckDfEraser, "realWeight","relValWU3_norm_mean", color_="red", ax=ax1)


ax2 = plot_test(sCheckDfWood,"realWeight","relValWU1_norm_std", color_="blue")
plot_test(sCheckDfWood,     "realWeight","relValWU2_norm_std", color_="blue", ax=ax2)
plot_test(sCheckDfWood,     "realWeight","relValWU3_norm_std", color_="blue", ax=ax2)

plot_test(sCheckDfEraser, "realWeight","relValWU1_norm_std", color_="red", ax=ax2)
plot_test(sCheckDfEraser, "realWeight","relValWU2_norm_std", color_="red", ax=ax2)
plot_test(sCheckDfEraser, "realWeight","relValWU3_norm_std", color_="red", ax=ax2)



ax3 = plot_test(sCheckDfWood,"realWeight","relValWU1_std", color_="blue")
plot_test(sCheckDfWood,     "realWeight","relValWU2_std", color_="blue", ax=ax3)
plot_test(sCheckDfWood,     "realWeight","relValWU3_std", color_="blue", ax=ax3)

plot_test(sCheckDfEraser, "realWeight","relValWU1_std", color_="red", ax=ax3)
plot_test(sCheckDfEraser, "realWeight","relValWU2_std", color_="red", ax=ax3)
plot_test(sCheckDfEraser, "realWeight","relValWU3_std", color_="red", ax=ax3)

"""

overallKPIsRawDataEraser = convert_df(sCheckDfEraser)
overallKPIsRawDataWood = convert_df(sCheckDfWood)

overallKPIsRawData = pd.concat([overallKPIsRawDataWood,overallKPIsRawDataEraser ])

fig, ax = plt.subplots(figsize=(10, 6))
sns.scatterplot(data=overallKPIsRawData, x="realWeight", y="norm_mean", hue="test", style="sensor", s=200)

fig, ax = plt.subplots(figsize=(10, 6))
sns.scatterplot(data=overallKPIsRawData, x="realWeight", y="norm_std", hue="test", style="sensor", s=200)



#%% Plotting of the batch

fig, axs = plt.subplots(3,1)

fig, axs2 = plt.subplots(2,2)

# fig, axs3 = plt.subplots(2,1)

figHisto, axsHisto = plt.subplots(1,1)

KPIs = pd.DataFrame(np.nan, index=range(len(allDfDualSensor)), columns=["run",
                                                                        "mean1", "std1", 
                                                                        "mean2", "std2", 
                                                                        "mean3", "std3", 
                                                                        "meanSum", "stdSum"])

for ii, df in enumerate(allDfDualSensor):
    
    ####################
    # Timeseries plots #
    ####################
    
    plt.sca(axs[0])
    # Plot of two sensors - normalized data !
    pltMain, = plt.plot(df["tBeforeMeasure1"]-df["tBeforeMeasure1"][0] ,  df["relativeVal_WU1"] , label="Sensor 1")
    plt.plot(df["tBeforeMeasure2"]-df["tBeforeMeasure2"][0] ,  df["relativeVal_WU2"] , label="Sensor 2", color = pltMain.get_color())
    plt.plot(df["tBeforeMeasure3"]-df["tBeforeMeasure3"][0] ,  df["relativeVal_WU3"] , label="Sensor 3", color = pltMain.get_color())
    plt.grid(True)
    plt.title("All relatives values")
    #plt.legend()
    plt.show()
    
    
    plt.sca(axs[1])
    # Plot of the sum of the two sensors
    plt.plot(df["tBeforeMeasure1"]-df["tBeforeMeasure1"][0],  df["relativeVal_WU1"] + df["relativeVal_WU2"] + df["relativeVal_WU3"], label="Sum", color = pltMain.get_color())
    plt.grid(True)
    #plt.legend()
    plt.title("Sum of all relatives values")
    plt.show()
    
    
    plt.sca(axs[2])
    # Plot of the mult of the two sensors
    #plt.plot(df["tBeforeMeasure1"]-df["tBeforeMeasure1"][0] ,  (df["realValue_WU1"] * df["realValue_WU2"]) , label="Skewness", color = pltMain.get_color())
    plt.plot(df["tBeforeMeasure1"]-df["tBeforeMeasure1"][0] ,  1-0.5*abs(df["realValue_WU1"] - df["realValue_WU2"])/(df["realValue_WU1"] + df["realValue_WU2"]) , label="Skewness", color = pltMain.get_color())
    plt.grid(True)
    #plt.legend()
    plt.show()

    ######################
    # Comparison sensors #
    ######################
    
   
    mtch = re.search(r"(\d*)gr_(\d)", fileNameList[ii])
    tag = "{:.0f} #{:d}".format(float(mtch.group(1)), int(mtch.group(2)))
    

    plt.sca(axs2[0,0])
    plt.scatter([tag]*len(df),  (df["relativeVal_WU1"]) , label="Sensor1", marker='o', s=60, color = pltMain.get_color())
    plt.scatter([tag]*len(df),  (df["relativeVal_WU2"]) , label="Sensor2", marker='x', s=40, color = pltMain.get_color())
    plt.scatter([tag]*len(df),  (df["relativeVal_WU3"]) , label="Sensor2", marker='d', s=40, color = pltMain.get_color())
    plt.grid(True)
    plt.xticks(rotation=45)
    #l1 = plt.legend(bbox_to_anchor=(1.04,1), borderaxespad=0)
    plt.subplots_adjust(right=0.8)
    plt.title("Comparison all sensors relative values")
    plt.show()
    
    plt.sca(axs2[0,1])
    plt.scatter([tag]*len(df), (df["relativeVal_WU1"]) , marker='o', label="Sensor1")
    plt.grid(True)
    plt.ylabel("Sensor 1")
    plt.xticks(rotation=45)
    plt.subplots_adjust(right=0.8)
    plt.title("Sensor 1 relative value")
    plt.show()
    
    plt.sca(axs2[1,0])
    plt.scatter([tag]*len(df), (df["relativeVal_WU2"]) ,  marker='x', label="Sensor2")
    plt.grid(True)
    plt.ylabel("Sensor 2")
    plt.xticks(rotation=45)
    plt.subplots_adjust(right=0.8)
    plt.title("Sensor 2 relative value")
    plt.show()
    
    plt.sca(axs2[1,1])
    plt.scatter([tag]*len(df), (df["relativeVal_WU3"]) ,  marker='d', label="Sensor3")
    plt.grid(True)
    plt.ylabel("Sensor 3")
    plt.xticks(rotation=45)
    plt.subplots_adjust(right=0.8)
    plt.title("Sensor 3 relative value")
    plt.show()
    
    
    ####################
    # KPIs calculation #
    ####################

    
    KPIs["run"].iloc[ii] = ii +1 
    KPIs["mean1"].iloc[ii] = np.mean(df["relativeVal_WU1"])
    KPIs["std1"].iloc[ii] = np.std(df["relativeVal_WU1"])
    
    KPIs["mean2"].iloc[ii] = np.mean(df["relativeVal_WU2"])
    KPIs["std2"].iloc[ii] = np.std(df["relativeVal_WU2"])
    
    KPIs["mean3"].iloc[ii] = np.mean(df["relativeVal_WU3"])
    KPIs["std3"].iloc[ii] = np.std(df["relativeVal_WU3"])
    
    KPIs["meanSum"].iloc[ii] = np.mean(df["relativeVal_WU1"] +df["relativeVal_WU1"])
    KPIs["stdSum"].iloc[ii] = np.std(df["relativeVal_WU1"] +df["relativeVal_WU1"])
    
    plt.sca(axsHisto)
    
    plt.hist((df["relativeVal_WU1"]-df["relativeVal_WU1"].mean())/50) # Being 50 a common value for the conversion between WU and gr
    plt.hist((df["relativeVal_WU2"]-df["relativeVal_WU2"].mean())/50)
    plt.hist((df["relativeVal_WU3"]-df["relativeVal_WU3"].mean())/50)
    plt.grid(True)
    
    
print(KPIs)


        


#%% Training - Data preparation


# Remove outlayers
"""
for ii, file in enumerate(fileNameList):
    testB1 = ( (allDfDualSensor[ii]["relativeVal_WU1"] > (KPIs["mean1"].iloc[ii] + 5*KPIs["std1"].iloc[ii]) ).any() or
               (allDfDualSensor[ii]["relativeVal_WU1"] < (KPIs["mean1"].iloc[ii] - 5*KPIs["std1"].iloc[ii]) ).any() )
    
    testB2 = ( (allDfDualSensor[ii]["relativeVal_WU2"] > (KPIs["mean2"].iloc[ii] + 5*KPIs["std2"].iloc[ii]) ).any() or
               (allDfDualSensor[ii]["relativeVal_WU2"] < (KPIs["mean2"].iloc[ii] - 5*KPIs["std2"].iloc[ii]) ).any() )
    
    testB3 = ( (allDfDualSensor[ii]["relativeVal_WU3"] > ((allDfDualSensor[ii]["relativeVal_WU3"]).median() + 5*KPIs["std3"].iloc[ii]) ).any() or
               (allDfDualSensor[ii]["relativeVal_WU3"] < ((allDfDualSensor[ii]["relativeVal_WU3"]).median() - 5*KPIs["std3"].iloc[ii]) ).any() )
    print(testB1 or testB2 or testB3)
    
    if testB1:
        print(ii)
        print(allDfDualSensor[ii]["relativeVal_WU1"] )
        break;
"""

dfTraining = pd.concat(allDfDualSensor, ignore_index=True) 


X = dfTraining[["relativeVal_WU1", "relativeVal_WU2", "relativeVal_WU3"]]
y = dfTraining["realWeight"]

Xfinal = X
yfinal = y

allData  = pd.concat([Xfinal, yfinal], axis=1)
Xarray = Xfinal.to_numpy()
yarray = yfinal.to_numpy()

from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

dt = DecisionTreeRegressor()
dt.fit(Xfinal, yfinal)
yhat = dt.predict(Xfinal)

r2_score(yfinal, yhat), mean_absolute_error(yfinal, yhat), np.sqrt(mean_squared_error(yfinal, yhat))
#r2_score(yfinal, yfinalPredPipe), mean_absolute_error(yfinal, yfinalPredPipe), np.sqrt(mean_squared_error(yfinal, yfinalPredPipe))



#%% Training - Pipeline with Poly Feat


from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from scipy.linalg import lstsq

from scipy.stats import norm
from scipy.stats import kurtosis, skew
import math

# Different options:
    
pipe = Pipeline([('PolyFeat',   PolynomialFeatures(degree=3, include_bias=True, interaction_only=False)), 
                 ('LinearReg',  LinearRegression())  ] )

"""
pipe = Pipeline([('PolyFeat',   PolynomialFeatures(degree=3, include_bias=True, interaction_only=False)), 
                 ('LinearReg',  LinearRegression())  ] )

pipe = Pipeline([('PolyFeat',   PolynomialFeatures(degree=2, include_bias=True, interaction_only=False)), 
                 ('LinearReg',  LinearRegression())  ] )

pipe = Pipeline([('PolyFeat',   PolynomialFeatures(degree=2, include_bias=True, interaction_only=True)), 
                 ('LinearReg',  LinearRegression())  ] )

"""

XfinalPipe = Xfinal[["relativeVal_WU1","relativeVal_WU2","relativeVal_WU3" ]]
pipe.fit(XfinalPipe, yfinal)

## NOTE !
"""
Remember for coeff interpretation that:
     - PolyFeat generates polynomial and interaction features such as this example:
      For [X1, X2, X3], you'll get [1 X1, X2, X3, X1*X2, X1*X3, X2*X3, X1*X2*X3 ]
      (this example only have the interactions !)
     
Also you could run:
     pipe.steps[0][1].get_feature_names_out()
      
More info here: https://scikit-learn.org/stable/modules/preprocessing.html#polynomial-features

"""

coefsPipe = modelPolyFeat["LinearReg"].coef_
interceptPipe = modelPolyFeat["LinearReg"].intercept_
print(modelPolyFeat.steps[0][1].get_feature_names_out())
print(coefsPipe)
print(interceptPipe)


origin = pd.DataFrame({'relativeVal_WU1': [0], 'relativeVal_WU2': [0], 'relativeVal_WU3': [0]})

"""
xLineSensor1 = pd.DataFrame({'relativeVal_WU1': np.linspace(0, 10000/3, 100), 
                            'relativeVal_WU2':  np.zeros(100),
                            'relativeVal_WU3':  np.zeros(100)})
xLineSensor2 = pd.DataFrame({'relativeVal_WU1': np.zeros(100), 
                            'relativeVal_WU2':  np.linspace(0, 10000/3, 100),
                            'relativeVal_WU3':  np.zeros(100)})
xLineSensor3 = pd.DataFrame({'relativeVal_WU1': np.zeros(100), 
                            'relativeVal_WU2':  np.zeros(100),
                            'relativeVal_WU3':  np.linspace(0, 10000/3, 100)})
xLineSensorAll = pd.DataFrame({'relativeVal_WU1': np.linspace(0, 10000/3, 100), 
                            'relativeVal_WU2':  np.linspace(0, 10000/3, 100),
                            'relativeVal_WU3':  np.linspace(0, 10000/3, 100)})
"""


XfinalPredPipe = XfinalPipe

yfinalPredPipe =  pipe.predict(XfinalPredPipe)

allDataPipe = allData.copy()
allDataPipe["predictWeight"] = yfinalPredPipe
allDataPipe["absError"] = allDataPipe["predictWeight"] - allDataPipe["realWeight"]
allDataPipe["relativeError"] = ( allDataPipe["predictWeight"] - allDataPipe["realWeight"])/ allDataPipe["realWeight"]


print("MAE:  {:.2f} gr".format(np.abs(allDataPipe["absError"]).mean()))
print("RMSE: {:.2f} gr".format(np.sqrt(((allDataPipe["absError"])**2).mean()  )) )
print("R:    {:.5f}".format(pipe.score(XfinalPipe, yfinal)))

print("MaxAE:  {:.2f} gr".format(np.abs(allDataPipe["absError"]).max()))

#  Plots
true_value = yfinal
predicted_value = yfinalPredPipe

plt.figure(figsize=(10,10))
plt.scatter(true_value, predicted_value, c='red')
plt.scatter(true_value, predictionsGenetic, c='green')

plt.scatter(0, pipe.predict(origin), c='orange')

#plt.yscale('log')
#plt.xscale('log')

p1 = max(max(predicted_value), max(true_value))
p2 = min(min(predicted_value), min(true_value))
plt.plot([p1, p2], [p1, p2], 'b-')
plt.xlabel('True Values', fontsize=15)
plt.ylabel('Predictions', fontsize=15)
plt.axis('equal')
plt.grid(True)
plt.show()

######################
##### Error plot #####
######################

plt.figure(figsize=(10,10))
plt.scatter(true_value, allDataPipe["absError"], c='red')
plt.scatter(true_value, error, c='green')


plt.xlabel('True Values [gr]', fontsize=15)
plt.ylabel('Absolute error [gr]', fontsize=15)
plt.grid(True)
plt.show()

plt.figure(figsize=(10,10))
plt.scatter(true_value, abs(allDataPipe["absError"]), c='red')
plt.xlabel('True Values [gr]', fontsize=15)
plt.ylabel('Absolute error [gr]', fontsize=15)
plt.grid(True)
plt.show()


#%% Analysis error

sns.pairplot(data=allDataPipe[[ "relativeVal_WU1", "relativeVal_WU2", "relativeVal_WU3", "absError"]], hue="absError")




#%%

weight_func = generate_weight_function(XfinalPipe, yfinal)


def predict_weight(df: pd.DataFrame, weight_func) -> pd.Series:
    X = df[["relativeVal_WU1", "relativeVal_WU2", "relativeVal_WU3"]]
    y_pred = []
    for _, row in X.iterrows():
        y_pred.append(weight_func(row.to_numpy()))
    return pd.Series(y_pred, index=df.index, name="predicted_weight")


# Predict weights
predictionsGenetic = predict_weight(XfinalPipe, weight_func)
error = predictionsGenetic-yfinal
error.describe()


#%% Export model

import pickle
EXPORT_NAME = os.path.join(maindir, "models", "PipeLine_3rDegree_0to10kg_ForTest2.plk")
pickle.dump(pipe, open(EXPORT_NAME, 'wb'))


