#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  1 23:34:53 2021

@author: enriquem
"""

import sys
import os
pyWoobyPath = os.path.join(os.path.split(os.getcwd())[0])
sys.path.append(pyWoobyPath)

from pyWooby import Wooby

import numpy as np

import matplotlib.pyplot as plt

#####################
### Reading the file
#####################

myWooby = Wooby()
fileFolder = "/Users/enriquem/Documents/HumanityLab/Wooby/Github/Python/datasets/Wooby1Calib"
fileName = "Clustering_1.txt"

WoobyDataFrame = myWooby.importCSV(fileName, fileFolder)

#####################
### Setting up the data
#####################

# Filtering with only stabilized values 
totalDf = WoobyDataFrame[WoobyDataFrame["bSync"]==False]
totalDf = totalDf.reset_index()

#####################
### Plots
#####################


## Comparison for all the filters
fig, ax1 = plt.subplots()

color = 'tab:red'
ax1.set_xlabel('time (ms)')
ax1.set_ylabel('raw measure', color=color)
ax1.plot(totalDf["timeNorm"]/1000, totalDf["realValue_WU"],        color=color, marker ="+")
ax1.tick_params(axis='y', labelcolor=color)

ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

color = 'tab:blue'
ax2.set_ylabel('Filtered values', color=color)  # we already handled the x-label with ax1
ax2.plot(totalDf["timeNorm"]/1000, totalDf["correctedValueFiltered"], color=color,  marker ="+")
ax2.tick_params(axis='y', labelcolor=color)


fig.tight_layout()  # otherwise the right y-label is slightly clipped
plt.grid()
plt.show()

#####################
### Clustering
#####################

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

n_clusters = 7

# Create the KMeans
kmeans = KMeans(n_clusters=n_clusters, random_state=0)

# Create the pipeline
WoobyPipeline = make_pipeline(kmeans)
WoobyPipelineData = make_pipeline(std_scaler, normalizer)

totalDfTrainSImple = totalDf[["realValue_WU", "thetadeg"]]
totalDfTrain = totalDf[["realValue_WU", "thetadeg", "phideg", "myTmp"]]

WoobyPipeline.fit(totalDfTrain)
labels = kmeans.labels_
totalDf["labels"] = labels


newTotalDfTrain = WoobyPipelineData.fit_transform(totalDfTrain)

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
plt.bar(features, pca.explained_variance_)
plt.xlabel('PCA feature')
plt.ylabel('variance')
plt.xticks(features)
plt.show()


#####################
### Plots labels
#####################

## Comparison labels and files over time

plt.figure()
sns.scatterplot(x=totalDf["timeNorm"] , y=totalDf["realValue_WU"], hue=totalDf["labels"], palette="deep")
plt.xlabel("Time (ms)")

#####################
### Correspondance class vs. real weight
#####################

# Create a value map dict for mapping specific values.
valmap = {0: 3000, 
          1: 6000,
          2:    0,
          3: 5000,
          4: 4000,
          5: 2000, 
          6: 1000}
# Apply the value map into a new column.
totalDf['realWeight'] = totalDf['labels'].map(valmap)



#####################
### Plots labels with real weight
#####################

plt.figure()
sns.scatterplot(x=totalDf["timeNorm"] , y=totalDf["realValue_WU"], hue=totalDf["realWeight"], palette="deep")
plt.grid() 


plt.figure()
sns.scatterplot(x=totalDf["realValue_WU"] , y=totalDf["realWeight"], hue=totalDf["realWeight"], palette="deep")
plt.grid() 

plt.figure()
plt.plot(totalDf["realValue_WU"] , totalDf["realWeight"], color=totalDf["thetadeg"])
plt.grid() 

#####################
### Basic calibration
#####################

X = np.array(totalDf["realValue_WU"]).reshape(-1, 1)
y = np.array(totalDf["realWeight"]).reshape(-1, 1)

linearRegCalib = myWooby.basicCalibration(totalDf)

# The coefficients & interception
coeffsreg = linearRegCalib.coef_
intercept = linearRegCalib.intercept_
score =     linearRegCalib.score(X, y)

errors = linearRegCalib.predict(X) - y
maxPositiveError = np.max(errors)
maxNegativeError = np.min(errors)

totalDf["errorBasicCalib"] = errors

##################################     
###      Tendency line (basic)     
################################## 


X_tend_line = np.array([ min(X), max(X)]).reshape((-1, 1))
y_tend_line = linearRegCalib.predict(X_tend_line)

##################################     
### Plotting of calibration        
################################## 

plt.figure()

sns.scatterplot(x=totalDf["realValue_WU"] , y=totalDf["realWeight"], hue=totalDf["realWeight"], palette="deep")
# Tendency line (basic)
plt.plot(X_tend_line, y_tend_line, color="black", alpha=0.5, linestyle ="--")
plt.plot(X_tend_line, y_tend_line + maxPositiveError, color="black", alpha=0.1, linestyle ="--")
plt.plot(X_tend_line, y_tend_line + maxNegativeError, color="black", alpha=0.1, linestyle ="--")

plt.xlabel('Relative measured weight (bits)')
plt.ylabel('Real weight (gr)')
plt.grid(True)
plt.title("Comparative plot for the calibration")
plt.show()


plt.figure()
sns.scatterplot(x=totalDf["realValue_WU"] , y=abs(totalDf["errorBasicCalib"]), hue=totalDf["realWeight"], palette="deep")
plt.xlabel('Relative measured weight (bits)')
plt.ylabel('Linear Regression error (gr)')
plt.grid(True)
plt.show()


plt.figure()
sns.scatterplot(x=abs(totalDf["thetadeg"]) , y=abs(totalDf["errorBasicCalib"]), hue=totalDf["realWeight"], palette="deep")
plt.xlabel('Theta (deg)')
plt.ylabel('Linear Regression error (gr)')
plt.grid(True)
plt.title("Error vs. theta")
plt.show()

plt.figure()
sns.scatterplot(x=abs(totalDf["phideg"]) , y=abs(totalDf["errorBasicCalib"]), hue=totalDf["realWeight"], palette="deep")
plt.xlabel('Phi (deg)')
plt.ylabel('Linear Regression error (gr)')
plt.grid(True)
plt.title("Error vs. phi")
plt.show()

plt.figure()
sns.scatterplot(x=abs(totalDf["myTmp"]) , y=abs(totalDf["errorBasicCalib"]), hue=totalDf["realWeight"], palette="deep")
plt.xlabel('Temp (C)')
plt.ylabel('Linear Regression error (gr)')
plt.grid(True)
plt.title("Error vs. temp")
plt.show()

