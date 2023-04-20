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
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import re

#%% Creation of the Serial communication

myWooby = Wooby()

myWooby.availablePorts()

portWooby =  '/dev/tty.usbserial-0001' 
baudRateWooby = 115200;
    
myWooby.setupSerial(portWooby, baudRateWooby)

myWooby.tare()


#%% Reading of a calibration point

N_MAX_MEASURES = 15
SUBSET = "WoobyTripleHX711" 
SOURCE = "SERIAL" # "TELNET" OR "SERIAL" 

REAL_WEIGHT = 500
# in gr
SUFFIX = "1"

EXPORT_FOLDER = "/Users/enriquem/Documents/HumanityLab/Wooby/GitHub3/Wooby/Python/datasets"
FILE_NAME = "{}_{}gr_{}.csv".format(SUBSET, REAL_WEIGHT, SUFFIX)
FILE_FOLDER = os.path.join(EXPORT_FOLDER, SUBSET)
                       
OVERWRITE = True

# 
# myWooby.tare()
#dfDualLoadCell = myWooby.readNTimes("SERIAL", N_MAX_MEASURES)

# Export
#myWooby.exportCSV(dfDualLoadCell, FILE_NAME, FILE_FOLDER, OVERWRITE)

#%% Reading of a calibration point - Loop

REAL_WEIGHT = 0  # in gr
N_TEST = 5

print("\n\nRemove everything from Wooby. ")
input("Once it's done press enter to continue...")

myWooby.tare()

dfTestForTare = myWooby.readNTimes("SERIAL", 1)

threshold = 200

if ( abs(dfTestForTare["relativeVal_WU1"][0]) > threshold) or  (abs(dfTestForTare["relativeVal_WU2"][0]) > threshold)  :
    print("\n\nERROR WITH THE TARE !! ")
    print("Measure sensor 1: {}".format(dfTestForTare["relativeVal_WU1"][0]))
    print("Measure sensor 2: {}".format(dfTestForTare["relativeVal_WU2"][0]))
    print("Measure sensor 2: {}".format(dfTestForTare["relativeVal_WU3"][0]))

else:
     print("\n\nGOOD TARE ! :) ")


for ii in range(N_TEST):
    
    print("\n\nPut the weight of {} gr for the run #{}".format(REAL_WEIGHT, ii+1))
    input("Once it's done, press enter to measure...")
    
    N_MAX_MEASURES = 15
    #SUBSET = "WoobyDualHX711_Final" 
    #SOURCE = "SERIAL" # "TELNET" OR "SERIAL" 
    
    
    FILE_NAME = "{}_{}gr_{}.csv".format(SUBSET, REAL_WEIGHT, ii+1)
    FILE_FOLDER = os.path.join(EXPORT_FOLDER, SUBSET)
                           
    OVERWRITE = True
    
    # 
    # myWooby.tare()
    dfDualLoadCell = myWooby.readNTimes("SERIAL", N_MAX_MEASURES)
    
    # Export
    myWooby.exportCSV(dfDualLoadCell, FILE_NAME, FILE_FOLDER, OVERWRITE)
    
    # 
    print("End of the run #{}".format(ii+1))
    
#exit()

#%% Plots for testing


fig, axs = plt.subplots(3,1)

plt.sca(axs[0])
# Plot of two sensors - normalized data !
plt.plot(dfDualLoadCell["tBeforeMeasure1"] ,  dfDualLoadCell["relativeVal_WU1"] , label="Sensor 1")
plt.plot(dfDualLoadCell["tBeforeMeasure2"] ,  dfDualLoadCell["relativeVal_WU2"] , label="Sensor 2")
plt.plot(dfDualLoadCell["tBeforeMeasure3"] ,  dfDualLoadCell["relativeVal_WU2"] , label="Sensor 3")
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

"""
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


# For different configurations study 

FILE_FOLDER = os.path.join("/Users/enriquem/Documents/HumanityLab/Wooby/GitHub2Test/Wooby/Python/datasets/", "WoobyDualHX711_Study_Configurations")

fileNameList1 = ["WoobyDualHX711_501gr_{}.csv".format(ii) for ii in range(1,6) ]
fileNameList2 = ["WoobyDualHX711_550gr_{}.csv".format(ii) for ii in range(1,6) ]


fileNameList3 = ["WoobyDualHX711_OuterPos_500gr_{}.csv".format(ii) for ii in range(1,6) ]
fileNameList4 = ["WoobyDualHX711_OuterPos_550gr_{}.csv".format(ii) for ii in range(1,6) ]


fileNameList5 = ["WoobyDualHX711_OuterPos_SamePlace_500gr_{}.csv".format(ii) for ii in range(1,6) ]
fileNameList6 = ["WoobyDualHX711_OuterPos_SamePlace_550gr_{}.csv".format(ii) for ii in range(1,6) ]


fileNameList =  fileNameList1 + fileNameList2 + fileNameList3 + fileNameList4 + fileNameList5 + fileNameList6


fileNameList = ["WoobyTripleHX711_500gr_{}.csv".format(ii) for ii in range(1,6) ]
"""


# For final configurations datasets 

FILE_FOLDER = os.path.join("/Users/enriquem/Documents/HumanityLab/Wooby/GitHub3/Wooby/Python/datasets", "WoobyTripleHX711ForTest2")

fileNameList = ["WoobyTripleHX711_700gr_{}.csv".format(ii) for ii in range(1,6) ]

fileNameList = ([ "WoobyTripleHX711_700gr_{}.csv".format(ii) for ii in range(1,6) ]  +
                [ "WoobyTripleHX711_500gr_{}.csv".format(ii) for ii in range(1,6) ]  +
                [ "WoobyTripleHX711_200gr_{}.csv".format(ii) for ii in range(1,6) ]  )

# For test with weights between 1 kg and 5 kg 

fileNameList = ([ "WoobyTripleHX711_0gr_{}.csv".format(ii) for ii in range(1,6) ]  +
                [ "WoobyTripleHX711_993gr_{}.csv".format(ii) for ii in range(1,6) ]  +
                [ "WoobyTripleHX711_2966gr_{}.csv".format(ii) for ii in range(1,6) ]  +
                [ "WoobyTripleHX711_4946gr_{}.csv".format(ii) for ii in range(1,6) ] +
                [ "WoobyTripleHX711ForTest_200gr_{}.csv".format(ii) for ii in range(1,2) ] +
                [ "WoobyTripleHX711ForTest_500gr_{}.csv".format(ii) for ii in range(1,2) ] +
                [ "WoobyTripleHX711ForTest_993gr_{}.csv".format(ii) for ii in range(1,2) ] +
                [ "WoobyTripleHX711ForTest_1981gr_{}.csv".format(ii) for ii in range(1,2) ] +
                [ "WoobyTripleHX711ForTest_2966gr_{}.csv".format(ii) for ii in range(1,2) ] +
                [ "WoobyTripleHX711ForTest_3956gr_{}.csv".format(ii) for ii in range(1,2) ] +
                [ "WoobyTripleHX711ForTest_4946gr_{}.csv".format(ii) for ii in range(1,2) ] +
                [ "WoobyTripleHX711ForTest_5941gr_{}.csv".format(ii) for ii in range(1,2) ] +
                [ "WoobyTripleHX711ForTest_6934gr_{}.csv".format(ii) for ii in range(1,2) ] +
                [ "WoobyTripleHX711ForTest_7925gr_{}.csv".format(ii) for ii in range(1,2) ] +
                [ "WoobyTripleHX711ForTest_8916gr_{}.csv".format(ii) for ii in range(1,2) ] +
                [ "WoobyTripleHX711ForTest_9912gr_{}.csv".format(ii) for ii in range(1,2) ] 
                )

# New batch with WoobyTripleHX711ForTest2
fileNameList     = ([ "WoobyTripleHX711ForTest2_0gr_{}.csv".format(ii) for ii in range(1,6) ]  +
                    [ "WoobyTripleHX711ForTest2_200gr_{}.csv".format(ii) for ii in range(1,6) ] +
                    [ "WoobyTripleHX711ForTest2_500gr_{}.csv".format(ii) for ii in range(1,6) ] +
                    [ "WoobyTripleHX711ForTest2_993gr_{}.csv".format(ii) for ii in range(1,6) ] +
                    [ "WoobyTripleHX711ForTest2_1981gr_{}.csv".format(ii) for ii in range(1,6) ] +
                    [ "WoobyTripleHX711ForTest2_2966gr_{}.csv".format(ii) for ii in range(1,6) ] +
                    [ "WoobyTripleHX711ForTest2_3956gr_{}.csv".format(ii) for ii in range(1,6) ] +
                    [ "WoobyTripleHX711ForTest2_4944gr_{}.csv".format(ii) for ii in range(1,6) ] +
                    [ "WoobyTripleHX711ForTest2_5939gr_{}.csv".format(ii) for ii in range(1,6) ] +
                    [ "WoobyTripleHX711ForTest2_6932gr_{}.csv".format(ii) for ii in range(1,6) ] +
                    [ "WoobyTripleHX711ForTest2_7923gr_{}.csv".format(ii) for ii in range(1,6) ] +
                    [ "WoobyTripleHX711ForTest2_8914gr_{}.csv".format(ii) for ii in range(1,6) ] +
                    [ "WoobyTripleHX711ForTest2_9910gr_{}.csv".format(ii) for ii in range(1,6) ] )

fileNameListTest = ([ "WoobyTripleHX711ForTest2_0gr_{}.csv".format(ii) for ii in range(1,6) ]  +
                    [ "WoobyTripleHX711ForTest2_200gr_{}.csv".format(ii) for ii in range(1,6) ] +
                    [ "WoobyTripleHX711ForTest2_500gr_{}.csv".format(ii) for ii in range(1,6) ] +
                    [ "WoobyTripleHX711ForTest2_993gr_{}.csv".format(ii) for ii in range(1,6) ] +
                    [ "WoobyTripleHX711ForTest2_1981gr_{}.csv".format(ii) for ii in range(1,6) ] +
                    [ "WoobyTripleHX711ForTest2_2966gr_{}.csv".format(ii) for ii in range(1,6) ] +
                    [ "WoobyTripleHX711ForTest2_3956gr_{}.csv".format(ii) for ii in range(1,6) ] +
                    [ "WoobyTripleHX711ForTest2_4944gr_{}.csv".format(ii) for ii in range(1,6) ] +
                    [ "WoobyTripleHX711ForTest2_5939gr_{}.csv".format(ii) for ii in range(1,6) ] +
                    [ "WoobyTripleHX711ForTest2_6932gr_{}.csv".format(ii) for ii in range(1,6) ] +
                    [ "WoobyTripleHX711ForTest2_7923gr_{}.csv".format(ii) for ii in range(1,6) ] +
                    [ "WoobyTripleHX711ForTest2_8914gr_{}.csv".format(ii) for ii in range(1,6) ] +
                    [ "WoobyTripleHX711ForTest2_9910gr_{}.csv".format(ii) for ii in range(1,6) ] )


"""
fileNameList = ([ "WoobyTripleHX711_0gr_{}.csv".format(ii) for ii in range(1,6) ]  +
                [ "WoobyTripleHX711ForTest_9912gr_{}.csv".format(ii) for ii in range(1,2) ] 
                )
"""

"""
fileNameList = ([ "WoobyTripleHX711_0gr_{}.csv".format(ii) for ii in range(1,6) ]  +
                [ "WoobyTripleHX711_993gr_{}.csv".format(ii) for ii in range(1,6) ]  +
                [ "WoobyTripleHX711_2966gr_{}.csv".format(ii) for ii in range(1,6) ]  +
                [ "WoobyTripleHX711_4946gr_{}.csv".format(ii) for ii in range(1,6) ]  +
                [ "WoobyTripleHX711_9912gr_{}.csv".format(ii) for ii in range(1,2) ] )

"""


"""
fileNameList = ([ "WoobyDualHX711_Final_70gr_{}.csv".format(ii) for ii in range(1,7) ]  +
                [ "WoobyDualHX711_Final_700gr_{}.csv".format(ii) for ii in range(1,7) ]  +
                [ "WoobyDualHX711_Final_2500gr_{}.csv".format(ii) for ii in range(1,7) ]  +
                [ "WoobyDualHX711_Final_2510gr_{}.csv".format(ii) for ii in range(1,7) ]  +
                [ "WoobyDualHX711_Final_3000gr_{}.csv".format(ii) for ii in range(1,7) ]  +
                [ "WoobyDualHX711_Final_3500gr_{}.csv".format(ii) for ii in range(1,7) ]  +
                [ "WoobyDualHX711_Final_3700gr_{}.csv".format(ii) for ii in range(1,7) ]  +
                [ "WoobyDualHX711_Final_4840gr_{}.csv".format(ii) for ii in range(1,7) ]  
                 )

"""


allDfDualSensor = myWooby.importCSVbatch(fileNameList, FILE_FOLDER)
allDfDualSensorTest = myWooby.importCSVbatch(fileNameListTest, FILE_FOLDER)


dfTotal = pd.DataFrame()
dfTest =  pd.DataFrame()
 
for ii, df in enumerate(allDfDualSensor):
    dfTotal= dfTotal.append(df, ignore_index=True)
    
for ii, df in enumerate(allDfDualSensorTest):
    dfTest= dfTest.append(df, ignore_index=True)
    

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

import re


for ii, file in enumerate(fileNameList):
    print(file)
    mtch = re.search(r"(\d*)gr", file)
    print(mtch.group(1))
    allDfDualSensor[ii]["realWeight"] = float(mtch.group(1))
    

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

# X["skewness"] = X["relativeVal_WU1"] * X["relativeVal_WU1"] /(X["relativeVal_WU1"] + X["relativeVal_WU1"] )
X["skewness"] = X["relativeVal_WU1"] * X["relativeVal_WU1"] 

# Suplementary mirrored data
"""
Xsup = X.copy()
Xsup["relativeVal_WU1"] = X["relativeVal_WU3"]

ysup = y
Xsup["relativeVal_WU3"] = X["relativeVal_WU1"]
"""

# Total data

"""
Xfinal = X.append(Xsup, ignore_index=True)
yfinal = y.append(ysup, ignore_index=True)
"""

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


#%% Supplement plots

"""
plt.figure()
plt.scatter(dfTraining["realWeight"], dfTraining["relativeVal_WU1"])
plt.scatter(dfTraining["realWeight"], dfTraining["relativeVal_WU2"])
plt.scatter(dfTraining["realWeight"], dfTraining["relativeVal_WU3"])
plt.grid(True)
plt.show()

plt.figure()
plt.scatter(dfTraining["relativeVal_WU1"], dfTraining["relativeVal_WU2"])
plt.xlabel('relativeVal_WU1')
plt.ylabel('relativeVal_WU2')
plt.grid(True)
plt.show()

plt.figure()
plt.scatter(dfTraining["relativeVal_WU1"], dfTraining["relativeVal_WU3"])
plt.xlabel('relativeVal_WU1')
plt.ylabel('relativeVal_WU2')
plt.grid(True)
plt.show()
"""

import seaborn as sns
sns.pairplot(data=dfTraining[["realWeight", "relativeVal_WU1", "relativeVal_WU2", "relativeVal_WU3"]], hue="realWeight")


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

coefsPipe = pipe["LinearReg"].coef_
interceptPipe = pipe["LinearReg"].intercept_
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
plt.xlabel('True Values [gr]', fontsize=15)
plt.ylabel('Absolute error [gr]', fontsize=15)
plt.grid(True)
plt.show()



#%% Export model

import pickle
EXPORT_NAME = os.path.join(maindir, "models", "PipeLine_3rDegree_0to10kg_ForTest2.plk")
pickle.dump(pipe, open(EXPORT_NAME, 'wb'))


