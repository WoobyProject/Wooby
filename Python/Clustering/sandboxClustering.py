#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 25 13:46:28 2021

@author: enriquem
"""

import sys
import os
pyWoobyPath =  os.path.join(os.path.split(os.getcwd())[0])
sys.path.append(pyWoobyPath)


import pyWooby
import pandas as pd

fileFolder = "/Users/enriquem/Documents/HumanityLab/Wooby/Github/Python/datasets/WOOBY2_CALIB_BOTTOM"

wo = pyWooby.Wooby()

listFiles = ["WOOBY2_CALIB_BOTTOM_50gr_BACK.txt",
             "WOOBY2_CALIB_BOTTOM_50gr_FLAT.txt",
             "WOOBY2_CALIB_BOTTOM_50gr_FRONT.txt",
             "WOOBY2_CALIB_BOTTOM_200gr_BACK.txt",
             "WOOBY2_CALIB_BOTTOM_200gr_FLAT.txt",
             "WOOBY2_CALIB_BOTTOM_200gr_FRONT.txt",
             "WOOBY2_CALIB_BOTTOM_500gr_BACK.txt",
             "WOOBY2_CALIB_BOTTOM_500gr_FLAT.txt",
             "WOOBY2_CALIB_BOTTOM_500gr_FRONT.txt"]

'''
listFiles = ["WOOBY2_CALIB_BOTTOM_50gr_FLAT.txt",
             "WOOBY2_CALIB_BOTTOM_200gr_FLAT.txt", 
             "WOOBY2_CALIB_BOTTOM_500gr_FLAT.txt", 
             "WOOBY2_CALIB_BOTTOM_1000gr_FLAT.txt"]
'''

listFolders = [fileFolder]*len(listFiles)

totalDf = pd.DataFrame()

for i,fileName in enumerate(listFiles):
    WoobyData = pyWooby.load.readWoobyFile(listFolders[i], fileName, verbose=True)
    WoobyData["data"]["file"] = i
    
    WoobyData["data"] = wo.extraCalcWooby(WoobyData["data"])
    print( WoobyData["data"]["timeNorm"])
    
    totalDf  = totalDf.append(WoobyData["data"], ignore_index=True)




###################



import seaborn as sns
import matplotlib.pyplot as plt


from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import Normalizer
from sklearn.pipeline import make_pipeline

# Create the std scaler
std_scaler = StandardScaler()

# Create the Normalizer 
normalizer = Normalizer()

n_clusters = int(2*len(listFiles)/3)

# Create the KMeans
kmeans = KMeans(n_clusters=6, random_state=0)

# Create the pipeline
WoobyPipeline = make_pipeline(std_scaler, kmeans)
WoobyPipelineData = make_pipeline(std_scaler)

totalDfTrainSimple = totalDf[["realValue_WU", "thetadeg"]]
totalDfTrain = totalDf[["realValue_WU", "thetadeg", "phideg", "myTmp"]]


labels = kmeans.labels_
totalDf["labels"] = labels



#####################
### Normalization and standarization
#####################


newTotalDfTrain = WoobyPipelineData.fit_transform(totalDfTrain)

for i in range(0,newTotalDfTrain.shape[1]):
    data1 = totalDfTrain.to_numpy()[0:,i] 
    data2 = newTotalDfTrain[0:,i]
    
    fig, ax1 = plt.subplots()
    
    color = 'tab:red'
    ax1.set_ylabel('Raw', color=color)
    ax1.plot(data1, color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    
    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    color = 'tab:blue'
    ax2.set_ylabel('Normalized', color=color)  # we already handled the x-label with ax1
    ax2.plot(data2, color=color)
    ax2.tick_params(axis='y', labelcolor=color)
    
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    ax1.set_title(totalDfTrain.keys()[i])
    plt.show()


def movingAvg(inputSignal, n):
    if not isinstance(inputSignal, pd.DataFrame):
        inputSignalSeries = pd.Series(inputSignal)
        
    resultFilter = inputSignalSeries.rolling(window=n).mean()
    
    return np.array(resultFilter)

myData =  newTotalDfTrain[0:,2]

plt.figure()
plt.plot(myData)
plt.plot( [np.mean(myData)]  * len(myData)  )  
mvgAvrg = movingAvg(myData, 8)
plt.plot(mvgAvrg)
mvgAvrg2 = movingAvg(myData, 16)
plt.plot(mvgAvrg2)
mvgAvrg3 = movingAvg(myData, 30)
plt.plot(mvgAvrg3)

#####################
### PCA
#####################

from sklearn.decomposition import PCA


pca = PCA(n_components=4)
pca_features = pca.fit_transform(newTotalDfTrain)

print("Mean")
print(pca.mean_)

print("Components")
print(pca.components_)


# Plot the explained variances
features = range(pca.n_components_)
plt.figure()
plt.bar(features, pca.explained_variance_)
plt.xlabel('PCA feature')
plt.ylabel('variance')
plt.xticks(features)
plt.show()


#####################
### Plots
#####################


# Crosscheck
cs = pd.crosstab(totalDf["file"], totalDf["labels"] )
print(cs)


# Crosscheck plot
plt.figure()
plt.scatter(totalDf["realValue_WU"], totalDf["realWeight"], c=labels, marker='+')


## Comparison labels and files over time
plt.figure()
plt.scatter(totalDf["timeNorm"], totalDf["realValue_WU"], c =totalDf["file"])

plt.figure()
plt.scatter(totalDf["timeNorm"], totalDf["realValue_WU"], c =totalDf["labels"])

plt.figure()
sns.scatterplot(x=totalDf["timeNorm"] , y=totalDf["realValue_WU"], hue=totalDf["labels"], palette="deep")


"""

plt.figure()
plt.scatter(labels, totalDf["file"], c=labels, marker='+')
plt.xlabel("labels")
plt.ylabel("file")

plt.figure()
plt.scatter(totalDf["timeSim"], totalDf["thetadeg"], c=labels, marker='+')
plt.xlabel("labels")
plt.ylabel("file")



#####
plt.figure()
plt.scatter(totalDf["timeNorm"], totalDf["file"], c=totalDf["file"])

plt.figure()
for i in range(0,4):
    filtDf = totalDf[totalDf["file"]==i]
    plt.scatter(filtDf["timeNorm"], filtDf["realValue_WU"],c=filtDf["labels"])
    
    
"""
