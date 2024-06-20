#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 23:07:12 2024

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
from pyWooby.filtering import *


import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.stats import norm
import re
import yaml

import seaborn as sns


from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.io as pio
pio.renderers.default='browser'

import plotly.graph_objects as go
from scipy.signal import butter, filtfilt, lfilter, lfilter_zi

#%% Initialization

## Initializing the Wooby element
myWooby = Wooby()

#%% Reading the file

def procees_data_baby(dataset_folder, file_name, t_start, t_end, filtering=True, realWeight=0):
    file_path =  os.path.join(dataset_folder, file_name)
    dfWooby = myWooby.process_file(file_path)
     
    
    #% New variables
    dfWooby["tBeforeMeasure1Norm"] = dfWooby["tBeforeMeasure1"] - dfWooby["tBeforeMeasure1"].iloc[0]
    dfWooby["tBeforeMeasure2Norm"] = dfWooby["tBeforeMeasure2"] - dfWooby["tBeforeMeasure2"].iloc[0]
    dfWooby["tBeforeMeasure3Norm"] = dfWooby["tBeforeMeasure3"] - dfWooby["tBeforeMeasure3"].iloc[0]
    dfWooby["tBeforeMeasure4Norm"] = dfWooby["tBeforeMeasure4"] - dfWooby["tBeforeMeasure4"].iloc[0]
    
    dfWooby["tAfterMeasure1Norm"] = dfWooby["tAfterMeasure1"] - dfWooby["tAfterMeasure1"].iloc[0]
    dfWooby["tAfterMeasure2Norm"] = dfWooby["tAfterMeasure2"] - dfWooby["tAfterMeasure2"].iloc[0]
    dfWooby["tAfterMeasure3Norm"] = dfWooby["tAfterMeasure3"] - dfWooby["tAfterMeasure3"].iloc[0]
    dfWooby["tAfterMeasure4Norm"] = dfWooby["tAfterMeasure4"] - dfWooby["tAfterMeasure4"].iloc[0]
    
    dfWooby["absoluteError"] = dfWooby["correctedValueFiltered"] - realWeight
     
    if filtering:
        dfWoobyFiltered = dfWooby[(dfWooby["tBeforeMeasure1Norm"] >= t_start)  & (dfWooby["tBeforeMeasure1Norm"] <= t_end)]
    else:
        dfWoobyFiltered = dfWooby
  

    return (dfWooby, dfWoobyFiltered)

def plotFinalDisplayedData(dfWoobyFiltered_, dfWooby_, title="", plotVar="correctedValueFiltered"):
    #% Plots
    
    if (type(dfWoobyFiltered_) == pd.DataFrame) :
        dfWooby_ = [dfWooby_]
        dfWoobyFiltered_ = [dfWoobyFiltered_]
    
            
    fig = go.Figure( layout=go.Layout(
            title=go.layout.Title(text=title)
        ) )
    
    for i in range(len(dfWooby_)):
        df = dfWooby_[i]
        dfFiltered = dfWoobyFiltered_[i]
        """
        fig.add_trace(go.Scatter(x=dfWoobyFiltered["tBeforeMeasure1Norm"], y=dfWoobyFiltered["realValueFiltered"],
                            mode='lines+markers',
                            name='realValueFiltered'))
        fig.add_trace(go.Scatter(x=dfWoobyFiltered["tBeforeMeasure1Norm"], y=dfWoobyFiltered["realValue"],
                            mode='lines+markers',
                            name='realValue'))
        """
        fig.add_trace(go.Scatter(x=df["tBeforeMeasure1Norm"], y=df[plotVar],
                            mode='lines+markers',
                            name=plotVar,  line=dict( color='rgba(135, 206, 250, 0.8)', dash='dot')))
        fig.add_trace(go.Scatter(x=dfFiltered["tBeforeMeasure1Norm"], y=dfFiltered[plotVar],
                            mode='lines+markers',
                            name=plotVar))
    fig.show()
    
    
def plotRawData(dfWoobyFiltered, dfWooby, title=""):
    fig2 = go.Figure( layout=go.Layout(
            title=go.layout.Title(text=title)
        ) )
    fig2.add_trace(go.Scatter(x=dfWoobyFiltered["tBeforeMeasure1Norm"], y=dfWoobyFiltered["realValue_WU1"],
                        mode='lines+markers',
                        name='realValue_WU1'))
    fig2.add_trace(go.Scatter(x=dfWoobyFiltered["tBeforeMeasure2Norm"], y=dfWoobyFiltered["realValue_WU2"],
                        mode='lines+markers',
                        name='realValue_WU2'))
    fig2.add_trace(go.Scatter(x=dfWoobyFiltered["tBeforeMeasure3Norm"], y=dfWoobyFiltered["realValue_WU3"],
                        mode='lines+markers',
                        name='realValue_WU3'))
    fig2.add_trace(go.Scatter(x=dfWoobyFiltered["tBeforeMeasure4Norm"], y=dfWoobyFiltered["realValue_WU4"],
                        mode='lines+markers',
                        name='realValue_WU4'))
    
    
    fig2.show()
    
    return fig2

def calculationKPI(dfWoobyFiltered):
    #% KPIs
    KPIs = pd.DataFrame()
    KPIs.loc[0,"std"]   = dfWoobyFiltered["correctedValueFiltered"].std()
    KPIs.loc[0,"mean"] = dfWoobyFiltered["correctedValueFiltered"].mean()
    
    return KPIs

#%%

from scipy.ndimage import median_filter
from scipy.ndimage import gaussian_filter
from scipy.signal import savgol_filter

def moving_average_filter(df, window_size):
    return df.rolling(window=window_size).mean()


def apply_median_filter(df, size):
    return median_filter(df, size=size)


def apply_gaussian_filter(df, sigma):
    return gaussian_filter(df, sigma=sigma)


def apply_savgol_filter(df, window_length, polyorder):
    return df.apply(lambda x: savgol_filter(x, window_length, polyorder))


def butter_lowpass_filter(data, cutoff, fs, order=5, initial_value=None):
    """
    Apply a low-pass Butterworth filter to the data using single-pass filtering with initial conditions.
    
    Parameters:
    data (array-like): The input data to filter.
    cutoff (float): The cutoff frequency of the filter.
    fs (float): The sampling frequency of the data.
    order (int): The order of the filter.
    initial_value (float): The initial value to initialize the filter.
    
    Returns:
    filtered_data (ndarray): The filtered data.
    """
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    
    if initial_value is not None:
        # Calculate the initial conditions for the filter
        zi = lfilter_zi(b, a) * initial_value
    else:
        # Default initial conditions based on the first value of the data
        zi = lfilter_zi(b, a) * data.iloc[0]
    
    filtered_data, _ = lfilter(b, a, data, zi=zi)
    return filtered_data


def exponential_moving_average(data, window):
    """
    Apply an exponential moving average filter to the data.
    
    Parameters:
    data (pd.Series): The input data to filter.
    window (int): The span or window size for the EMA.
    
    Returns:
    ema (pd.Series): The filtered data.
    """
    alpha = 2 / (window + 1.0)

    ema = np.zeros(len(data))
    ema[0] = data.iloc[0]  # Initialize with the first data point
    for i in range(1, len(data)):
        ema[i] = alpha * data.iloc[i] + (1 - alpha) * ema[i - 1]
    return pd.Series(ema, index=data.index)

#%% Running analysis

babyCase = "babyB"

if babyCase == "babyA":
    dataset_folder = os.path.join(maindir, "datasets/WoobyBabyA")
    allFilesNames = ["beforefeeding_two_one.txt",   "beforefeeding_one_one.txt",    "beforefeeding_test.txt"]
    allTStart =     [3e3,                           0,                              3e3]
    allTEnd  =      [50e3,                          13e3,                           50e3]
    filtering = True
elif babyCase == "babyB":
    dataset_folder = os.path.join(maindir, "datasets/WoobyBabyB")
    allFilesNames = ["BB_beforefeeding_clothes_one_one.txt",    "BB_beforefeeding_clothes_one_two.txt", "BB_beforefeeding_noclothes_one_one.txt",       "BB_beforefeeding_noclothes_one_two.txt",  \
                     "BB_afterfeeding_noclothes_one_one.txt",        "BB_afterfeeding_noclothes_two_one.txt",]
    allTStart =     [3e3,                             0,                                0,                              3e3,   \
                     0,                               0 ]
    allTEnd  =      [60e3,                           60e3,                             60e3,                           60e3,  \
                     60e3,                           60e3]
    filtering = False
else:
    print("Not a valid option")
    
# Create final report
report = pd.DataFrame()
report["name"] = allFilesNames
allKPIs =  pd.DataFrame()
allDf = list()
allDfFiltered = list()

# Iterate over the datasets
for iF in range(len(allFilesNames)):
    # Case selection 
    file_name = allFilesNames[iF]
    t_start = allTStart[iF]
    t_end = allTEnd[iF]
    
    # Evaluation
    dfWooby, dfWoobyFiltered = procees_data_baby(dataset_folder, file_name, t_start,  t_end, filtering=True, realWeight=4180.47)
    plotRawData(dfWoobyFiltered, dfWooby, title = file_name)
    plotFinalDisplayedData(dfWoobyFiltered, dfWooby, title = file_name)
    KPIs = calculationKPI(dfWoobyFiltered)
    
    # Total variables constructions
    allDf.append(dfWooby)
    allDfFiltered.append(dfWoobyFiltered)
    allKPIs = pd.concat([allKPIs, KPIs], ignore_index=True)


    
report = pd.concat([report, allKPIs], axis=1, join="inner")
print(report)


#%% Plots of all the measurements


plotFinalDisplayedData(allDfFiltered, allDf, title = "All file measurements", plotVar="correctedValueFiltered")
# plotFinalDisplayedData(allDfFiltered, allDf, title = "All file measurements", plotVar="absoluteError")
# plotFinalDisplayedData(allDfFiltered, allDf, title = "All file measurements", plotVar="bSync")

#%% 

clothesWeight = report["mean"][0] - report["mean"][2:4].mean()
foodWeight = report["mean"][4:6].mean() - report["mean"][2:4].mean()

#%% Time evaluation

iF = 1
df = allDf[iF]

# Plot the results
fig = go.Figure()
          
# Original data
fig.add_trace(go.Scatter(x=df['tBeforeMeasure1'], y=1+0*df['tBeforeMeasure1'], mode='markers', name='tBeforeMeasure1', line=dict(dash='dash')))
fig.add_trace(go.Scatter(x=df['tBeforeMeasure2'], y=2+0*df['tBeforeMeasure2'], mode='markers', name='tBeforeMeasure2', line=dict(dash='dash')))
fig.add_trace(go.Scatter(x=df['tBeforeMeasure3'], y=3+0*df['tBeforeMeasure3'], mode='markers', name='tBeforeMeasure3', line=dict(dash='dash')))
fig.add_trace(go.Scatter(x=df['tBeforeMeasure4'], y=4+0*df['tBeforeMeasure4'], mode='markers', name='tBeforeMeasure4', line=dict(dash='dash')))

fig.add_trace(go.Scatter(x=df['tAfterMeasure1'], y=1+0*df['tAfterMeasure1'], mode='markers', name='tAfterMeasure1', line=dict(dash='dash')))
fig.add_trace(go.Scatter(x=df['tAfterMeasure2'], y=2+0*df['tAfterMeasure2'], mode='markers', name='tAfterMeasure2', line=dict(dash='dash')))
fig.add_trace(go.Scatter(x=df['tAfterMeasure3'], y=3+0*df['tAfterMeasure3'], mode='markers', name='tAfterMeasure3', line=dict(dash='dash')))
fig.add_trace(go.Scatter(x=df['tAfterMeasure4'], y=4+0*df['tAfterMeasure4'], mode='markers', name='tAfterMeasure4', line=dict(dash='dash')))

fig.add_trace(go.Scatter(x=df['tAfterAlgo1'], y=1+0*df['tAfterAlgo1'], mode='markers', name='tAfterAlgo1', line=dict(dash='dash')))
fig.add_trace(go.Scatter(x=df['tAfterAlgo2'], y=2+0*df['tAfterAlgo2'], mode='markers', name='tAfterAlgo2', line=dict(dash='dash')))
fig.add_trace(go.Scatter(x=df['tAfterAlgo3'], y=3+0*df['tAfterAlgo3'], mode='markers', name='tAfterAlgo3', line=dict(dash='dash')))
fig.add_trace(go.Scatter(x=df['tAfterAlgo4'], y=4+0*df['tAfterAlgo4'], mode='markers', name='tAfterAlgo4', line=dict(dash='dash')))

fig.show()

# Average sample time 
print(df['tBeforeMeasure1'].diff().mean())
print(df['tBeforeMeasure2'].diff().mean())
print(df['tBeforeMeasure3'].diff().mean())
print(df['tBeforeMeasure4'].diff().mean())

# Average measurement time per sensor
print( (df['tAfterMeasure1'] - df['tBeforeMeasure1']).mean())
print( (df['tAfterMeasure2'] - df['tBeforeMeasure2']).mean())
print( (df['tAfterMeasure3'] - df['tBeforeMeasure3']).mean())
print( (df['tAfterMeasure4'] - df['tBeforeMeasure4']).mean())

# Total average measurement time
print( (df['tAfterMeasure4'] - df['tBeforeMeasure1']).mean())

#%% Sandbox-  All algorithms

iF = 5
df = allDf[iF]
dfValid = allDfFiltered[iF]

window_size = 5
median_size = 5
gaussian_sigma = 2
savgol_window_length = 7
savgol_polyorder = 2

fs = 1/1.13
cutoff = 0.08*(fs)

dfValid['moving_average'] = moving_average_filter(dfValid['correctedValueFiltered'], window_size)
dfValid['median'] = apply_median_filter(dfValid['correctedValueFiltered'], median_size)
dfValid['gaussian'] = apply_gaussian_filter(dfValid['correctedValueFiltered'], gaussian_sigma)

dfValid['butter_lowpass_filter'] = butter_lowpass_filter(dfValid['correctedValueFiltered'], cutoff, fs, order=6)
dfValid['exp_moving_average'] = exponential_moving_average(dfValid['correctedValueFiltered'], window_size)

"""
dfValid['savgol'] = apply_savgol_filter(dfValid['correctedValueFiltered'], savgol_window_length, savgol_polyorder)
"""

# Plot the results
fig = go.Figure()

# Original data
fig.add_trace(go.Scatter(x=df['tAfterMeasure4Norm'], y=df['correctedValueFiltered'], mode='markers+lines', name='Original', line=dict(color='gray', dash='dot')))

# Original data
fig.add_trace(go.Scatter(x=dfValid['tAfterMeasure4Norm'], y=dfValid['correctedValueFiltered'], mode='markers+lines', name='Valid', line=dict(color='gray', dash='dash')))

# Moving Average Filter
fig.add_trace(go.Scatter(x=dfValid['tAfterMeasure4Norm'], y=dfValid['moving_average'], mode='markers+lines', name='Moving Average'))

# Median Filter
fig.add_trace(go.Scatter(x=dfValid['tAfterMeasure4Norm'], y=dfValid['median'], mode='markers+lines', name='Median Filter'))

# Gaussian Filter
fig.add_trace(go.Scatter(x=dfValid['tAfterMeasure4Norm'], y=dfValid['gaussian'], mode='markers+lines', name='Gaussian Filter'))

# Butter lowpass filter
fig.add_trace(go.Scatter(x=dfValid['tAfterMeasure4Norm'], y=dfValid['butter_lowpass_filter'], mode='markers+lines', name='Butter Lowpass Filter'))

# EMA
fig.add_trace(go.Scatter(x=dfValid['tAfterMeasure4Norm'], y=dfValid['exp_moving_average'], mode='markers+lines', name='EMAvg'))


"""
# Savitzky-Golay Filter
fig.add_trace(go.Scatter(x=dfValid['time'], y=dfValid['savgol'], mode='lines', name='Savitzky-Golay Filter'))
"""
fig.show()


print("{}: {:.2f} gr".format("correctedValueFiltered",     dfValid['correctedValueFiltered'].std())    )
print("{}: {:.2f} gr".format("moving_average",             dfValid['moving_average'].std())            )
print("{}: {:.2f} gr".format("median",                     dfValid['median'].std())                    )
print("{}: {:.2f} gr".format("gaussian",                   dfValid['gaussian'].std())                  )
print("{}: {:.2f} gr".format("butter_lowpass_filter",      dfValid['butter_lowpass_filter'].std())     )
print("{}: {:.2f} gr".format("exp_moving_average",         dfValid['exp_moving_average'].std())        )

#%% Sandbox-  Test Moving Avg

report["std_moving_average5"] = [np.nan]*len(allDfFiltered)
report["std_moving_average6"] = [np.nan]*len(allDfFiltered)
report["std_moving_average4"] = [np.nan]*len(allDfFiltered)
report["std_moving_average10"] = [np.nan]*len(allDfFiltered)


for window_size in [4, 5, 6, 10]:
   
    
    # Iterate over the datasets
    for iF in range(len(allDfFiltered)):
        
        df = allDfFiltered[iF]
        
        keyMvgAvg = 'moving_average{}'.format(window_size)
        df[keyMvgAvg] = moving_average_filter(df['correctedValueFiltered'], window_size)
        df['median'] = apply_median_filter(df['correctedValueFiltered'], median_size)
        df['gaussian'] = apply_gaussian_filter(df['correctedValueFiltered'], gaussian_sigma)
        """
        df['savgol'] = apply_savgol_filter(df['correctedValueFiltered'], savgol_window_length, savgol_polyorder)
        """
    
        report["std_"+keyMvgAvg][iF] =   df[keyMvgAvg].std()
        

print(report[["std", "std_moving_average4"]])
print(report[["std", "std_moving_average5"]])
print(report[["std", "std_moving_average6"]])
print(report[["std", "std_moving_average10"]])



# Plot the results
fig = go.Figure()
   
for iF in range(len(allDfFiltered)):
    df = allDfFiltered[iF]
 
    # Original data
    fig.add_trace(go.Scatter(x=df['tAfterMeasure4Norm'], y=df['correctedValueFiltered'], mode='lines', name='Original', line=dict(color='gray', dash='dash')))
    
    for window_size in [10]:
       
        keyMvgAvg = 'moving_average{}'.format(window_size)
        # Moving Average Filter
        fig.add_trace(go.Scatter(x=df['tAfterMeasure4Norm'], y=df[keyMvgAvg], mode='lines', name=keyMvgAvg))
      
        
    
fig.show()
          
