#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  4 18:43:29 2021

@author: enriquem
"""


import sys
import os

maindir = maindir = "C:/Users/pasca/Wooby/devs/Python/"
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

portWooby =  'COM3'
baudRateWooby = 115200;

myWooby.setupSerial(portWooby, baudRateWooby)

myWooby.tare()

#%% Real time plotting

# Create figure for plotting
import matplotlib.gridspec as gridspec
fig = plt.figure()
gs = gridspec.GridSpec(2, 2)
ax = fig.add_subplot(gs[0, :])
ax_s1 = fig.add_subplot(gs[1, 0])
ax_s2 = fig.add_subplot(gs[1, 1])
ax2 = ax.twinx()
xs = [] #store trials here (n)
ys1 = [] #store relative frequency here
ys2 = []
cvF = []

# This function is called periodically from FuncAnimation
def animate(i, xs, ys1, ys2, cvF, myWooby):
    # Aquire and parse data from serial port
    """
    line = ser.readline()  # ascii
    line_as_list = line.split(b',')
    i = int(line_as_list[0])
    relProb = line_as_list[1]
    relProb_as_list = relProb.split(b'\n')
    relProb_float = float(relProb_as_list[0])
    """
    dfDualLoadCell = myWooby.readNTimes("SERIAL", 1)

    # Add x and y to lists
    xs.append(dfDualLoadCell['tBeforeMeasure1']/1000)
    ys1.append(dfDualLoadCell['relativeVal_WU1'])  # realValue_WU1
    ys2.append(dfDualLoadCell['relativeVal_WU2'])
    cvF.append(dfDualLoadCell['correctedValueFiltered'])

    # Limit x and y lists to 20 items
    # xs = xs[-20:]
    # ys = ys[-20:]

    # Draw x and y lists
    ax.clear()
    ax_s1.clear()
    ax_s2.clear()
    ax.plot(xs, ys1, label="Sensor 1", c="blue")
    ax.plot(xs, ys2, label="Sensor 2", c="orange")
    ax_s1.plot(xs, ys1, label="Sensor 1", c="blue")
    ax_s2.plot(xs, ys2, label="Sensor 2", c="orange")

    ax2.clear()
    ax2.plot(xs,cvF, 'r', label="Display value")
    #ax.plot(xs, rs, label="Theoretical Probability")

    # Format plot
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)
    plt.title('Title to be customized')
    plt.ylabel('Sensor WU')
    plt.legend()
    ax.grid(True)
    ax_s1.grid(True)
    ax_s2.grid(True)
    # plt.axis([1, None, 0, 1.1])  # Use for arbitrary number of trials
    # plt.axis([1, 100, 0, 1.1]) #Use for 100 trial demo


# Set up plot to call animate() function periodically
ani = animation.FuncAnimation(fig, animate, fargs=(xs, ys1, ys2, cvF, myWooby), interval=1500)
plt.show()

