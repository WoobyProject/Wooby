#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  1 23:34:53 2021

@author: enriquem
"""

#####################
### Reading the file
#####################

# TODO !

#####################
### Setting up the data
#####################

# Filtering with only stabilized values 
totalDf = WoobyDataFrame[WoobyDataFrame["bSync"]==False]
totalDf = totalDf.reset_index()

#####################
### Plots
#####################

import matplotlib.pyplot as plt

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

n_clusters = 4

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
### Plots
#####################

## Comparison labels and files over time

plt.figure()
sns.scatterplot(x=totalDf["timeNorm"] , y=totalDf["realValue_WU"], hue=totalDf["labels"], palette="deep")


#####################
### Correspondance class vs. real weight
#####################

# Create a value map dict for mapping specific values.
valmap = {0: 4000, 1: 1000, 2:3000, 3:2000 }
# Apply the value map into a new column.
totalDf['realWeight'] = totalDf['labels'].map(valmap)



#####################
### Plots
#####################

plt.figure()
sns.scatterplot(x=totalDf["timeNorm"] , y=totalDf["realValue_WU"], hue=totalDf["realWeight"], palette="deep")



plt.figure()
sns.scatterplot(x=totalDf["realValue_WU"] , y=totalDf["realWeight"], hue=totalDf["realWeight"], palette="deep")


