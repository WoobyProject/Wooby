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
import pandas as pd
import numpy as np

#%% Creation of the Serial communication

myWooby = Wooby()

myWooby.availablePorts()

portWooby =  '/dev/tty.usbserial-0001' 
baudRateWooby = 115200;
    
myWooby.setupSerial(portWooby, baudRateWooby)

myWooby.tare()

#%% Reading of a calibration point

N_MAX_MEASURES = 15
SUBSET = "WoobyDualHX711_Final" 
SOURCE = "SERIAL" # "TELNET" OR "SERIAL" 

REAL_WEIGHT = 4840      # in gr
SUFFIX = "1"

FILE_NAME = "{}_{}gr_{}.csv".format(SUBSET, REAL_WEIGHT, SUFFIX)
FILE_FOLDER = os.path.join("/Users/enriquem/Documents/HumanityLab/Wooby/GitHub2Test/Wooby/Python/datasets/", SUBSET)
                       
OVERWRITE = True

# 
# myWooby.tare()
dfDualLoadCell = myWooby.readNTimes("SERIAL", N_MAX_MEASURES)

# Export
myWooby.exportCSV(dfDualLoadCell, FILE_NAME, FILE_FOLDER, OVERWRITE)

#%% Reading of a calibration point - Loop

REAL_WEIGHT = 700  # in gr

print("\n\nRemove everything from Wooby. ")
input("Once it's done press enter to continue...")

myWooby.tare()

dfTestForTare = myWooby.readNTimes("SERIAL", 1)

threshold = 200

if ( abs(dfTestForTare["relativeVal_WU1"][0]) > threshold) or  (abs(dfTestForTare["relativeVal_WU2"][0]) > threshold)  :
    print("\n\nERROR WITH THE TARE !! ")
    print("Measure sensor 1: {}".format(dfTestForTare["relativeVal_WU1"][0]))
    print("Measure sensor 2: {}".format(dfTestForTare["relativeVal_WU2"][0]))

else:
     print("\n\nGOOD TARE ! :) ")


for ii in range(6):
    
    print("\n\nPut the weight of {} gr for the run #{}".format(REAL_WEIGHT, ii+1))
    input("Once it's done, press enter to measure...")
    
    N_MAX_MEASURES = 15
    SUBSET = "WoobyDualHX711_Final" 
    SOURCE = "SERIAL" # "TELNET" OR "SERIAL" 
    
    
    FILE_NAME = "{}_{}gr_{}.csv".format(SUBSET, REAL_WEIGHT, ii+1)
    FILE_FOLDER = os.path.join("/Users/enriquem/Documents/HumanityLab/Wooby/GitHub2Test/Wooby/Python/datasets/", SUBSET)
                           
    OVERWRITE = True
    
    # 
    # myWooby.tare()
    dfDualLoadCell = myWooby.readNTimes("SERIAL", N_MAX_MEASURES)
    
    # Export
    myWooby.exportCSV(dfDualLoadCell, FILE_NAME, FILE_FOLDER, OVERWRITE)
    
    # 
    print("End of the run #{}".format(ii+1))
    


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

fileNameList = ["WoobyDualHX711_1000gr_CENTER.csv",
                "WoobyDualHX711_1000gr_LEFT.csv",
                "WoobyDualHX711_1000gr_RIGHT.csv",
                "WoobyDualHX711_1000gr_MID_LEFT.csv",
                "WoobyDualHX711_1000gr_MID_RIGHT.csv",
                ]


fileNameList = ["WoobyDualHX711_2050gr_{}.csv".format(ii) for ii in range(1,6) ]
# fileNameList = ["WoobyDualHX711_2000gr_{}.csv".format(ii) for ii in range(1,6) ]
# fileNameList = ["WoobyDualHX711_500gr_{}.csv".format(ii) for ii in range(1,6) ]
fileNameList = ["WoobyDualHX711_501gr_{}.csv".format(ii) for ii in range(1,6) ]
fileNameList = ["WoobyDualHX711_550gr_{}.csv".format(ii) for ii in range(1,6) ]


"""
# For different configurations study 

FILE_FOLDER = os.path.join("/Users/enriquem/Documents/HumanityLab/Wooby/GitHub2Test/Wooby/Python/datasets/", "WoobyDualHX711_Study_Configurations")

fileNameList1 = ["WoobyDualHX711_501gr_{}.csv".format(ii) for ii in range(1,6) ]
fileNameList2 = ["WoobyDualHX711_550gr_{}.csv".format(ii) for ii in range(1,6) ]


fileNameList3 = ["WoobyDualHX711_OuterPos_500gr_{}.csv".format(ii) for ii in range(1,6) ]
fileNameList4 = ["WoobyDualHX711_OuterPos_550gr_{}.csv".format(ii) for ii in range(1,6) ]


fileNameList5 = ["WoobyDualHX711_OuterPos_SamePlace_500gr_{}.csv".format(ii) for ii in range(1,6) ]
fileNameList6 = ["WoobyDualHX711_OuterPos_SamePlace_550gr_{}.csv".format(ii) for ii in range(1,6) ]


fileNameList =  fileNameList1 + fileNameList2 + fileNameList3 + fileNameList4 + fileNameList5 + fileNameList6
"""

# For final configurations datasets 

FILE_FOLDER = os.path.join("/Users/enriquem/Documents/HumanityLab/Wooby/GitHub2Test/Wooby/Python/datasets/", "WoobyDualHX711_Final")

fileNameList = ([ "WoobyDualHX711_Final_70gr_{}.csv".format(ii) for ii in range(1,7) ]  +
                [ "WoobyDualHX711_Final_700gr_{}.csv".format(ii) for ii in range(1,7) ]  +
                [ "WoobyDualHX711_Final_2500gr_{}.csv".format(ii) for ii in range(1,7) ]  +
                [ "WoobyDualHX711_Final_2510gr_{}.csv".format(ii) for ii in range(1,7) ]  +
                [ "WoobyDualHX711_Final_3000gr_{}.csv".format(ii) for ii in range(1,7) ]  +
                [ "WoobyDualHX711_Final_3500gr_{}.csv".format(ii) for ii in range(1,7) ]  +
                [ "WoobyDualHX711_Final_3700gr_{}.csv".format(ii) for ii in range(1,7) ]  +
                [ "WoobyDualHX711_Final_4840gr_{}.csv".format(ii) for ii in range(1,7) ]  
                 )


allDfDualSensor = myWooby.importCSVbatch(fileNameList, FILE_FOLDER)

#%% Plotting of the batch

fig, axs = plt.subplots(3,1)

fig, axs2 = plt.subplots(2,1)

fig, axs3 = plt.subplots(2,1)


KPIs = pd.DataFrame(np.nan, index=range(len(allDfDualSensor)), columns=["run", "mean1", "std1", "mean2", "std2", "meanSum", "stdSum"])

for ii, df in enumerate(allDfDualSensor):
    
    plt.sca(axs[0])
    # Plot of two sensors - normalized data !
    pltMain, = plt.plot(df["tBeforeMeasure1"]-df["tBeforeMeasure1"][0] ,  df["relativeVal_WU1"] , label="Sensor 1")
    plt.plot(df["tBeforeMeasure2"]-df["tBeforeMeasure2"][0] ,  df["relativeVal_WU2"] , label="Sensor 2", color = pltMain.get_color())
    plt.grid(True)
    plt.legend()
    plt.show()
    
    
    plt.sca(axs[1])
    # Plot of the sum of the two sensors
    plt.plot(df["tBeforeMeasure1"]-df["tBeforeMeasure1"][0],  df["relativeVal_WU1"] + df["relativeVal_WU2"] , label="Sum", color = pltMain.get_color())
    plt.grid(True)
    plt.legend()
    plt.show()
    
    
    plt.sca(axs[2])
    # Plot of the mult of the two sensors
    #plt.plot(df["tBeforeMeasure1"]-df["tBeforeMeasure1"][0] ,  (df["realValue_WU1"] * df["realValue_WU2"]) , label="Skewness", color = pltMain.get_color())
    plt.plot(df["tBeforeMeasure1"]-df["tBeforeMeasure1"][0] ,  1-0.5*abs(df["realValue_WU1"] - df["realValue_WU2"])/(df["realValue_WU1"] + df["realValue_WU2"]) , label="Skewness", color = pltMain.get_color())
    plt.grid(True)
    plt.legend()
    plt.show()


    plt.sca(axs2[0])
    plt.scatter([fileNameList[ii]]*len(df),  (df["relativeVal_WU1"]) , label="Sensor1", marker='o', s=60, color = pltMain.get_color())
    plt.scatter([fileNameList[ii]]*len(df),  (df["relativeVal_WU2"]) , label="Sensor2", marker='x', s=40, color = pltMain.get_color())
    plt.grid(True)
    l1 = plt.legend(bbox_to_anchor=(1.04,1), borderaxespad=0)
    plt.subplots_adjust(right=0.8)
    plt.show()
    
    plt.sca(axs2[1])
    plt.scatter([fileNameList[ii]]*len(df), ((df["relativeVal_WU1"]) + (df["relativeVal_WU2"]) )*(500/23200) , label="Sensor1")
    plt.grid(True)
    l1 = plt.legend(bbox_to_anchor=(1.04,1), borderaxespad=0)
    plt.subplots_adjust(right=0.8)
    plt.show()
    
    # KPIs calculation 
    
    KPIs["run"].iloc[ii] = ii +1 
    KPIs["mean1"].iloc[ii] = np.mean(df["relativeVal_WU1"])
    KPIs["std1"].iloc[ii] = np.std(df["relativeVal_WU1"])
    
    KPIs["mean2"].iloc[ii] = np.mean(df["relativeVal_WU2"])
    KPIs["std2"].iloc[ii] = np.std(df["relativeVal_WU2"])
    
    KPIs["meanSum"].iloc[ii] = np.mean(df["relativeVal_WU1"] +df["relativeVal_WU1"])
    KPIs["stdSum"].iloc[ii] = np.std(df["relativeVal_WU1"] +df["relativeVal_WU1"])
    
    
print(KPIs)



#%% Training - Data preration

import re


for ii, file in enumerate(fileNameList):
    print(file)
    mtch = re.search(r"(\d*)gr", file)
    print(mtch.group(1))
    allDfDualSensor[ii]["realWeight"] = float(mtch.group(1))
    
    
dfTraining = pd.concat(allDfDualSensor, ignore_index=True) 


X = dfTraining[["relativeVal_WU1", "relativeVal_WU2"]]
y = dfTraining["realWeight"]

# X["skewness"] = X["relativeVal_WU1"] * X["relativeVal_WU1"] /(X["relativeVal_WU1"] + X["relativeVal_WU1"] )
X["skewness"] = X["relativeVal_WU1"] * X["relativeVal_WU1"] 

# Suplementary mirrored data
Xsup = X.copy()
Xsup["relativeVal_WU1"] = X["relativeVal_WU2"]
Xsup["relativeVal_WU2"] = X["relativeVal_WU1"]

ysup = y

# Total data

Xfinal = X.append(Xsup, ignore_index=True)
yfinal = y.append(ysup, ignore_index=True)

allData  = pd.concat([Xfinal, yfinal], axis=1)
Xarray = Xfinal.to_numpy()
yarray = yfinal.to_numpy()

#%% Training - Pipeline with Poly Feat


from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression

pipe = Pipeline([('PolyFeat', PolynomialFeatures(2)), 
                 ('LinearReg', LinearRegression())  ] )


XfinalPipe = Xfinal[["relativeVal_WU1","relativeVal_WU2"]]
pipe.fit(XfinalPipe, yfinal)


coefsPipe = pipe["LinearReg"].coef_
interceptPipe = pipe["LinearReg"].intercept_
print(coefsPipe)
print(interceptPipe)


yfinalPredPipe =  pipe.predict(XfinalPipe)

allDataPipe = allData.copy()
allDataPipe["predictWeight"] = yfinalPredPipe
allDataPipe["absError"] = allDataPipe["predictWeight"] - allDataPipe["realWeight"]
allDataPipe["relativeError"] = ( allDataPipe["predictWeight"] - allDataPipe["realWeight"])/ allDataPipe["realWeight"]


print("MAE: {} gr".format(np.abs(allDataPipe["absError"]).mean()))
print("RMSE: {} gr".format(np.sqrt(((allDataPipe["absError"])**2).mean()  )) )
print("R: {}".format(pipe.score(XfinalPipe, yfinal)))



#  Plots
true_value = yfinal
predicted_value = yfinalPredPipe

plt.figure(figsize=(10,10))
plt.scatter(true_value, predicted_value, c='crimson')
plt.yscale('log')
plt.xscale('log')

p1 = max(max(predicted_value), max(true_value))
p2 = min(min(predicted_value), min(true_value))
plt.plot([p1, p2], [p1, p2], 'b-')
plt.xlabel('True Values', fontsize=15)
plt.ylabel('Predictions', fontsize=15)
plt.axis('equal')
plt.show()


#%% Linear regression 


reg = LinearRegression()
reg.fit(Xfinal, yfinal)


coefs = reg.coef_
intercept = reg.intercept_
print(coefs)
print(intercept)


# Make predictions using the testing set
yfinalPred = reg.predict(Xfinal)

allData["predictWeight"] = yfinalPred
allData["absError"] = allData["predictWeight"] - allData["realWeight"]
allData["relativeError"] = ( allData["predictWeight"] - allData["realWeight"])/ allData["realWeight"]

# Scores
absError = abs(yfinal-yfinalPred)
relativeError = (yfinal-yfinalPred)/yfinal
    
print("MAE: {} gr".format(np.abs(allData["absError"]).mean()))
print("RMSE: {} gr".format(np.sqrt(((allData["absError"])**2).mean()  )) )
print("R: {}".format(reg.score(Xfinal, yfinal)))


#  Plots

true_value = yfinal
predicted_value = yfinalPred

plt.figure(figsize=(10,10))
plt.scatter(true_value, predicted_value, c='crimson')
plt.yscale('log')
plt.xscale('log')

p1 = max(max(predicted_value), max(true_value))
p2 = min(min(predicted_value), min(true_value))
plt.plot([p1, p2], [p1, p2], 'b-')
plt.xlabel('True Values', fontsize=15)
plt.ylabel('Predictions', fontsize=15)
plt.axis('equal')
plt.show()


"""
plt.figure()
dataOK = allData[allData["absError"] < 20.0]
dataKO = allData[allData["absError"] >= 20.0]

plt.scatter(dataOK["relativeVal_WU1"],dataOK["relativeVal_WU2"], c="green")
plt.scatter(dataKO["relativeVal_WU1"],dataKO["relativeVal_WU2"], c="red")
plt.axis('equal')
plt.show()
"""

#%% Plots


plt.figure()
plt.plot(allDataPipe["absError"], label = "Pipeline")
plt.plot(allData["absError"], label = "Linear Regression")
plt.legend()
plt.show()

plt.figure()
plt.hist(allDataPipe["absError"], label = "Pipeline",       bins=np.arange(-30, 40, 5)-2.5, alpha=0.5)
plt.hist(allData["absError"], label = "Linear Regression",  bins=np.arange(-30, 40, 5)-2.5, alpha=0.5)
plt.legend()
plt.show()

import seaborn as sns
sns.set_theme(style="ticks")


plt.figure()
sns.pairplot(allData, hue="realWeight")


plt.figure()
sns.set_theme(style="darkgrid")

g = sns.jointplot(x="relativeVal_WU1", y="realWeight", data=allData,
                  kind="reg", truncate=False,
                 #xlim=(0, 60), ylim=(0, 12),
                  color="m", height=7)

# %%

from sklearn.decomposition import PCA

pca = PCA(n_components=2).fit(Xarray)

plt.scatter(Xarray[:, 0], Xarray[:, 1], s=100, alpha=0.8, label="samples")

for i, (comp, var) in enumerate(zip(pca.components_, pca.explained_variance_)):
    comp = comp * var  # scale component by its variance explanation power
    plt.plot(
        [0, comp[0]],
        [0, comp[1]],
        label=f"Component {i}",
        linewidth=2,
        color=f"C{i + 2}",
    )
plt.gca().set(
    aspect="equal",
    title="2-dimensional dataset with principal components",
    xlabel="first feature",
    ylabel="second feature",
)
plt.legend()
plt.show()


