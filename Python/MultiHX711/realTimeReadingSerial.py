#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  4 18:43:29 2021

@author: enriquem
"""


import sys
import os
import pickle

maindir = maindir = "/Users/enriquem/Documents/HumanityLab/Wooby/GitHub3/Wooby/Python"
print(maindir)
pckgdir = os.path.realpath(os.path.join(maindir, "pyWooby"))
sys.path.append(maindir)
print(pckgdir)


from pyWooby import Wooby

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style

#%% Creation of the Serial communication

myWooby = Wooby()

myWooby.availablePorts()

portWooby =   '/dev/tty.usbserial-0001' #'COM3'
baudRateWooby = 115200;

myWooby.setupSerial(portWooby, baudRateWooby)

myWooby.tare()

#%% Real time plotting


# Create figure for plotting
import matplotlib.gridspec as gridspec
fig = plt.figure()
gs = gridspec.GridSpec(2, 3)
ax = fig.add_subplot(gs[0, :])
ax_s1 = fig.add_subplot(gs[1, 0])
ax_s2 = fig.add_subplot(gs[1, 1])
ax_s3 = fig.add_subplot(gs[1, 2])
ax2 = ax.twinx()
xs = [] #store trials here (n)
ys1 = [] #store relative frequency here
ys2 = []
ys3 = []
cvF = []
calc = 0
Xpredict =  np.array([[0, 0, 0]])

dfLiveRead = pd.DataFrame()

# Possibility to load an existing ML model
IMPORT_NAME = os.path.join(maindir, "models", "PipeLine_OnlyInteractions_3rDegree.plk")
loaded_model = pickle.load(open(IMPORT_NAME, 'rb'))


# This function is called periodically from FuncAnimation
def animate(i, xs, ys1, ys2, ys3, cvF, myWooby):
    
    # Aquire and parse data from serial port
    """
    line = ser.readline()  # ascii
    line_as_list = line.split(b',')
    i = int(line_as_list[0])
    relProb = line_as_list[1]
    relProb_as_list = relProb.split(b'\n')
    relProb_float = float(relProb_as_list[0])
    """
    
    
    dfLiveRead = myWooby.readNTimes("SERIAL", 1)
    
    # Add x and y to lists
    xs.append(dfLiveRead['tBeforeMeasure1']/1000)
    ys1.append(dfLiveRead['relativeVal_WU1'])  # realValue_WU1
    ys2.append(dfLiveRead['relativeVal_WU2'])
    ys3.append(dfLiveRead['relativeVal_WU3'])
    
    calc =  ( 20.524596747258954 + 
            0.01906163*dfLiveRead['relativeVal_WU1'] 
            -0.02171782*dfLiveRead['relativeVal_WU2']  
            -0.02045766*dfLiveRead['relativeVal_WU3'])
    
    
    Xpredict[0][0]=dfLiveRead['relativeVal_WU1'][0]
    Xpredict[0][1]=dfLiveRead['relativeVal_WU2'][0]
    Xpredict[0][2]=dfLiveRead['relativeVal_WU3'][0]

    
    calc = loaded_model.predict(Xpredict)
    
    """
    print("\n")
    print("\n")
    print(dfLiveRead['relativeVal_WU1'][0])
    print("\n")
    print("\n")
    """
    
    calc = np.max([calc, 0.0])
    
    # cvF.append(dfLiveRead['correctedValueFiltered'])
    cvF.append(calc)
    
    # Limit x and y lists to 20 items
    # xs = xs[-20:]
    # ys = ys[-20:]

    # Draw x and y lists
    ax.clear()
    ax_s1.clear()
    ax_s2.clear()
    ax_s3.clear()
    """
    ax.plot(xs, ys1,    label="Sensor 1", c="blue")
    ax.plot(xs, ys2,    label="Sensor 2", c="red")
    ax.plot(xs, ys3,    label="Sensor 3", c="green")
    """
    ax_s1.plot(xs, ys1, label="Sensor 1", c="blue")
    ax_s2.plot(xs, ys2, label="Sensor 2", c="red")
    ax_s3.plot(xs, ys3, label="Sensor 3", c="green")
    ax2.clear()
    
        
    ax.plot(xs,cvF, 'o--', label="Display value")
    #ax.plot(xs, rs, label="Theoretical Probability")

    # Format plot
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)
    plt.title("Current weight: {:.3f}".format(calc))
    plt.ylabel('Sensor WU')
    ax.set_ylabel("Final weight")
    plt.legend()
    ax.grid(True)
    ax_s1.grid(True)
    ax_s2.grid(True)
    ax_s3.grid(True)
    # plt.axis([1, None, 0, 1.1])  # Use for arbitrary number of trials
    # plt.axis([1, 100, 0, 1.1]) #Use for 100 trial demo


# Set up plot to call animate() function periodically
ani = animation.FuncAnimation(fig, animate, fargs=(xs, ys1, ys2, ys3, cvF, myWooby), interval=1500)
plt.show()


#%% Post processing after real time plotting

time = [x.values[0] for x in xs] 
vec_relativeVal_WU1 = [x.values[0] for x in ys1]
vec_relativeVal_WU2 = [x.values[0] for x in ys2]
vec_relativeVal_WU3 = [x.values[0] for x in ys3]
# finalWeight =  [x.values[0] for x in cvF]
finalWeight = cvF

    

