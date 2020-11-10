#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 22 20:39:42 2020

@author: enriquem
"""

import serial
import os
import pandas as pd 
import numpy as np
from timeit import default_timer as timer
import matplotlib.pyplot as plt
import math

print("\nCalibration for Wooby\n")

def tare():
    serialPortWooby.write('t'.encode())

##########################        
# Serial connexion setup #
##########################

print("Connecting with Wooby ...")

portWooby = '/dev/cu.SLAB_USBtoUART'
baudRateWooby = 115200;

serialPortWooby = serial.Serial(port = portWooby, baudrate=baudRateWooby,
                           bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE)

serialPortWooby.reset_input_buffer()
serialPortWooby.reset_output_buffer()
serialPortWooby.flush()

serialPortWooby.flushInput()
serialPortWooby.flushOutput()

N_MAX_MEASURES = 400

# Measures configuration 
REAL_WEIGHT = 104
# SUBSET = "UNITARY_TEST"
SUBSET = "Austin" # "Austin"
SUFFIX = "Up_Box_Empty_Stormy"

##########################        
#  Serial data reading   #
##########################

# Reading the data
print("Reading serial data from Wooby ...")

i = 0
WoobyDataFrame = pd.DataFrame()


while (i < N_MAX_MEASURES):
    
    # Serial read section
    tStart = timer()
    dataLineWoobyRaw =  serialPortWooby.readline()
    tEnd = timer()
    # print("Reading time: {} ms".format((tEnd - tStart)*1000))
    # print("Inwaiting: {} bytes".format(serialPortWooby.inWaiting()))
    
    if ( (tEnd - tStart) < 0.500 ):
        continue
    
    try: 
        dataLineWooby = dataLineWoobyRaw.decode('Ascii')
    except:
         print("Cannot read line. Skipping... ")
         
    if (dataLineWooby.startswith('WS')!=True):
        print("Not a complete line or not a measurement line. Skipping... ")
        print(dataLineWooby)
        continue
    
    
    dataLineWooby = dataLineWooby[2:]    
    dataLineWoobyArray = dataLineWooby.split(",\t");
    tags = []
    values = []
    
    for varCouple in dataLineWoobyArray[0:-1]:
        varCoupleSplit = varCouple.split(":")
        tags.append(varCoupleSplit[0])
        values.append(float(varCoupleSplit[1]))
    
    df = pd.DataFrame([values], columns = tags)
    
    '''
    print(tags)
    print(values)
    print(df)
    '''
    
    WoobyDataFrame = WoobyDataFrame.append(df,ignore_index=True)
    
    # print("{}% ".format(int(100*i/N_MAX_MEASURES)), end="", flush=True)
    i = i + 1
    print("Line read! ({}/{}) Read time: {:.2f} ms".format(i, N_MAX_MEASURES, (tEnd - tStart)*1000 ))
   

# Closing the serial port would restart the Wooby (not wanted)
# serialPortWooby.close()

print(WoobyDataFrame.head())
print(WoobyDataFrame.keys())

###########################        
#      Calculations       #
###########################

## Adding the real weight
WoobyDataFrame["realWeight"] = [REAL_WEIGHT] * WoobyDataFrame.shape[0]

WoobyDataFrame["timeNorm"] = WoobyDataFrame["tBeforeMeasure"]-WoobyDataFrame["tBeforeMeasure"][0]
WoobyDataFrame["timeMeasure"] = WoobyDataFrame["tAfterMeasure"]-WoobyDataFrame["tBeforeMeasure"]
WoobyDataFrame["timeAlgo"] = WoobyDataFrame["tAfterAlgo"]-WoobyDataFrame["tAfterMeasure"]

WoobyDataFrame["timeSim"] = np.linspace(WoobyDataFrame["timeNorm"][0], WoobyDataFrame["timeNorm"].values[-1], WoobyDataFrame["timeNorm"].shape[0])
# WoobyDataFrame["Te"] =  WoobyDataFrame["timeSim"][1] -  WoobyDataFrame["timeSim"][0]

np.mean(np.diff(WoobyDataFrame["timeNorm"]))

'''

WoobyDataFrame["relativeValue_WU"] = WoobyDataFrame["realValue_WU"]-WoobyDataFrame["OFFSET"]

WoobyDataFrame["myAx"] = WoobyDataFrame["Ax"]/16384
WoobyDataFrame["myAy"] = WoobyDataFrame["Ay"]/16384
WoobyDataFrame["myAz"] = WoobyDataFrame["Az"]/16384

WoobyDataFrame["myGx"] = WoobyDataFrame["Gx"]/131
WoobyDataFrame["myGy"] = WoobyDataFrame["Gy"]/131
WoobyDataFrame["myGz"] = WoobyDataFrame["Gz"]/131
'''

###########################        
# Formatting and storing  #
###########################


fileName = "{}_{}gr_{}.txt".format(SUBSET, REAL_WEIGHT, SUFFIX)
fileFolder = os.path.join("/Users/macretina/Documents/Airbus/Humanity Lab/Wooby/Github/Python/datasets", SUBSET)
fileFullPath = os.path.join(fileFolder, fileName)

# Check if the folder exists
if os.path.isdir(fileFolder) == False :
    os.mkdir(fileFolder)

# Check if the file exists
if os.path.isfile(fileFullPath):
    print("File already exists")
else:
    fileWooby = open(fileFullPath, "w")
    fileWooby.write(WoobyDataFrame.to_csv(index=False))
    fileWooby.close()


###########################        
#     Additional plots    #
###########################

# WoobyDataFrame = readWoobyFile(fileFolder, fileName)["data"]

### Time recalculation
    plt.figure()
    plt.plot(WoobyDataFrame["timeNorm"], WoobyDataFrame["timeSim"] )
    plt.title("Evaluation of time correction for simulation ")
    plt.ylabel("Real normalize time (ms)")
    plt.xlabel("Simulation time (ms)")
    plt.grid(True)

    plt.figure()
    plt.plot(WoobyDataFrame["timeNorm"], (WoobyDataFrame["timeSim"]/WoobyDataFrame["timeNorm"] - 1)*100 )
    plt.title("Error in time correction for simulation ")
    plt.ylabel("Delta in time (%)")
    plt.xlabel("Simulation time (ms)")
    plt.grid(True)
    
     
### Performance in time

    plt.figure()
    plt.plot(WoobyDataFrame["timeNorm"][1:], np.diff(WoobyDataFrame["timeNorm"]) )
    plt.title("Speed per sample analysis")
    plt.ylabel("Speed per sample (ms/sample)")
    plt.xlabel("Time (ms)")
    plt.grid(True)
    
    plt.figure()
    plt.plot(WoobyDataFrame["timeNorm"], WoobyDataFrame["timeMeasure"],  label="Measurement")
    plt.plot(WoobyDataFrame["timeNorm"], WoobyDataFrame["timeAlgo"],     label="Algorithm")
    plt.title("Times comparison")
    plt.ylabel("Times (ms)")
    plt.xlabel("Time (ms) ")
    plt.legend(loc="best")
    plt.grid(True)


### Temperature analysis

    # Plot: Temperature vs time
    plt.figure()
    plt.plot(WoobyDataFrame["timeNorm"], WoobyDataFrame["myTmp"])
    plt.show()
    plt.grid(True)
    plt.title("Temperature over time")
    plt.xlabel("Time (ms)")
    plt.ylabel("Temperature (C) ")
    
    
    # Plot: Temperature vs relativeVal_WU
    plt.figure()
    plt.plot(WoobyDataFrame["myTmp"], WoobyDataFrame["relativeVal_WU"], 'o')
    plt.show()
    plt.grid(True)
    plt.title("Temperature vs measurement")
    plt.ylabel("Raw weight value (wu)")
    plt.xlabel("Temperature (C) ")



plt.figure()
plt.plot(WoobyDataFrame["timeNorm"], WoobyDataFrame["realValue_WU"])
plt.show()
plt.grid(True)

plt.figure()
plt.plot(WoobyDataFrame["timeNorm"], WoobyDataFrame["thetadeg"], label ="thetadeg")
plt.plot(WoobyDataFrame["timeNorm"], WoobyDataFrame["phideg"], label ="phideg")
plt.show()
plt.grid(True)


plt.figure()

plt.plot(WoobyDataFrame["timeNorm"], WoobyDataFrame["realValue"]-1003,             label="realValue")
plt.plot(WoobyDataFrame["timeNorm"], WoobyDataFrame["realValueFiltered"]-1003,     label="realValueFiltered")
plt.plot(WoobyDataFrame["timeNorm"], WoobyDataFrame["correctedValueFiltered"]-1003,label="correctedValueFiltered")
plt.legend(loc='best')
plt.grid(True)
plt.show()


plt.figure()
condensed = WoobyDataFrame["realValue"].append(WoobyDataFrame["realValueFiltered"]).append(WoobyDataFrame["correctedValueFiltered"])
minVal = math.floor(min(condensed)) 
maxVal = math.ceil(max(condensed))
bins = np.arange(minVal, maxVal, 0.25)
plt.hist(WoobyDataFrame["realValue"],               bins=bins, alpha=0.5, ec='black', label="realValue")
plt.hist(WoobyDataFrame["realValueFiltered"],       bins=bins, alpha=0.5, ec='black', label="realValueFiltered")
plt.hist(WoobyDataFrame["correctedValueFiltered"],  bins=bins, alpha=0.5, ec='black', label="correctedValueFiltered")
plt.legend(loc='best')
plt.grid(True)
plt.show()


plt.figure()
condensed = WoobyDataFrame["realValue"].append(WoobyDataFrame["realValueFiltered"]).append(WoobyDataFrame["correctedValueFiltered"])
minVal = math.floor(min(condensed)) 
maxVal = math.ceil(max(condensed))
bins = np.arange(minVal, maxVal, 0.25)
plt.hist(WoobyDataFrame["realValue"],               bins=bins, alpha=0.5, ec='black', label="realValue")
plt.hist(WoobyDataFrame["realValueFiltered"],       bins=bins, alpha=0.5, ec='black', label="realValueFiltered")
plt.legend(loc='best')
plt.grid(True)
plt.show()







thetaVec = np.linspace(min(WoobyDataFrame["thetadeg"]), max(WoobyDataFrame["thetadeg"]), 20)
W0 = max(WoobyDataFrame["relativeVal_WU"])

plt.figure()
newPythonCalc = (1/SLOPE_basic)*WoobyDataFrame["relativeVal_WU"]/(1 + m_b_Xtreme*WoobyDataFrame["thetadeg"] + m_a_Xtreme*1.0*((WoobyDataFrame["thetadeg"]+0)**2))
rawVal = (1/SLOPE_basic)*WoobyDataFrame["relativeVal_WU"]
newWoobyCalc = (1/SLOPE_basic)*WoobyDataFrame["realValue_WU_AngleAdj"]
plt.plot(WoobyDataFrame["thetadeg"], newPythonCalc, linestyle="", marker='o', label="Angle adj (Python)")
plt.plot(WoobyDataFrame["thetadeg"], rawVal,        linestyle="", marker='o', label="Raw value")
plt.plot(WoobyDataFrame["thetadeg"], newWoobyCalc,  linestyle="", marker='o', label="Angle adj value")

plt.plot(thetaVec,                   (1/SLOPE_basic)*W0*(1+m_a*1.0*((thetaVec)**2)))
plt.legend(loc='best')
plt.grid(True)
plt.show()

plt.figure()
error_newPythonCalc = newPythonCalc-WoobyDataFrame["realWeight"]
error_rawVal = rawVal-WoobyDataFrame["realWeight"]
error_newWoobyCalc = newWoobyCalc-WoobyDataFrame["realWeight"]
bins = np.linspace(-25,25,50)

plt.hist(error_newPythonCalc,   bins=bins, alpha=0.5, label="Angle adj (Python)")
#plt.hist(error_rawVal,          bins=bins, alpha=0.5, label="Raw value ")
plt.hist(error_newWoobyCalc,    bins=bins, alpha=0.5, label="Angle adj value")
'''
plt.plot(newPythonCalc-WoobyDataFrame["realWeight"],    linestyle="", marker='o', label="Angle adj (Python)")
plt.plot(rawVal-WoobyDataFrame["realWeight"],           linestyle="", marker='o', label="Raw value")
plt.plot(newWoobyCalc-WoobyDataFrame["realWeight"],     linestyle="", marker='o', label="Angle adj value")
'''
plt.legend(loc='best')
plt.grid(True)
plt.show()

print("New error: {}".format(np.sum(error_newPythonCalc**2)))









plt.figure()
sns.scatterplot(WoobyDataFrame["thetadeg"], (1/SLOPE_basic)*WoobyDataFrame["relativeVal_WU"]/(1+m_a*1.0*((WoobyDataFrame["thetadeg"])**2)),        hue=WoobyDataFrame["thetadeg"], marker='o', label="Raw value (Python)")
sns.scatterplot(WoobyDataFrame["thetadeg"], (1/SLOPE_basic)*WoobyDataFrame["relativeVal_WU"],                                                      hue=WoobyDataFrame["thetadeg"], marker='o', label="Raw value")
sns.scatterplot(WoobyDataFrame["thetadeg"], (1/SLOPE_basic)*WoobyDataFrame["realValue_WU_AngleAdj"],                                               hue=WoobyDataFrame["thetadeg"], marker='o', label="Angle adj value")
plt.grid(True)


plt.figure()
plt.plot(WoobyDataFrame["thetadeg"], WoobyDataFrame["realValue_WU"], 'o', label="Raw value")
plt.plot(WoobyDataFrame["thetadeg"], WoobyDataFrame["realValue_WU_AngleAdj"],  'o', label="Angle adj value")
plt.legend(loc='best')
plt.grid(True)
plt.show()


plt.figure()
plt.plot(WoobyDataFrame["realValue_WU"], label="Raw vallue")
plt.plot(WoobyDataFrame["realValue_WU_AngleAdj"], label="Angle adj vallue")
plt.legend(loc='best')
plt.grid(True)
plt.show()




# Accelerations
plt.figure()
plt.plot(WoobyDataFrame["timeNorm"], WoobyDataFrame["myAx"], label="Ax")
plt.plot(WoobyDataFrame["timeNorm"], WoobyDataFrame["myAy"], label="Ay")
plt.plot(WoobyDataFrame["timeNorm"], WoobyDataFrame["myAz"], label="Az")
plt.legend(loc='best')
plt.grid(True)
plt.show()

plt.figure()
plt.plot(WoobyDataFrame["timeNorm"], WoobyDataFrame["myGx"], label="Gx")
plt.plot(WoobyDataFrame["timeNorm"], WoobyDataFrame["myGy"], label="Gy")
plt.plot(WoobyDataFrame["timeNorm"], WoobyDataFrame["myGz"], label="Gz")
plt.legend(loc='best')
plt.grid(True)
plt.show()



plt.figure()
plt.plot(WoobyDataFrame["myAx"], WoobyDataFrame["realValue_WU"], 'o', label="Ax")
plt.legend(loc='best')
plt.grid(True)
plt.show()


plt.figure()
plt.plot(WoobyDataFrame["relativeVal_WU"], -WoobyDataFrame["thetadeg"]/max(abs(WoobyDataFrame["thetadeg"])), 'o', label="theta norm")
plt.plot(WoobyDataFrame["relativeVal_WU"], WoobyDataFrame["myAx"]/max(abs(WoobyDataFrame["myAx"])), 'o', label="Ax norm")
plt.plot(WoobyDataFrame["relativeVal_WU"], WoobyDataFrame["myAy"]/max(abs(WoobyDataFrame["myAy"])), 'o', label="Ay norm")
plt.plot(WoobyDataFrame["relativeVal_WU"], WoobyDataFrame["myAz"]/max(abs(WoobyDataFrame["myAz"])), 'o', label="Az norm")
plt.legend(loc='best')
plt.grid(True)
plt.show()

plt.figure()
plt.plot(WoobyDataFrame["relativeVal_WU"], WoobyDataFrame["myAx"], 'o', label="Ax norm")
plt.plot(WoobyDataFrame["relativeVal_WU"], WoobyDataFrame["myAy"], 'o', label="Ay norm")
plt.plot(WoobyDataFrame["relativeVal_WU"], WoobyDataFrame["myAz"], 'o', label="Az norm")
plt.legend(loc='best')
plt.grid(True)
plt.show()


plt.figure()
plt.plot(WoobyDataFrame["relativeVal_WU"], WoobyDataFrame["myGx"], 'o', label="Gx norm")
plt.plot(WoobyDataFrame["relativeVal_WU"], WoobyDataFrame["myGy"], 'o', label="Gy norm")
plt.plot(WoobyDataFrame["relativeVal_WU"], WoobyDataFrame["myGz"], 'o', label="Gz norm")
plt.legend(loc='best')
plt.grid(True)
plt.show()


plt.figure()
plt.plot(WoobyDataFrame["relativeVal_WU"], -WoobyDataFrame["thetadeg"]/max(abs(WoobyDataFrame["thetadeg"])), 'o', label="theta norm")
plt.plot(WoobyDataFrame["relativeVal_WU"], WoobyDataFrame["myGx"]/max(abs(WoobyDataFrame["myGx"])), 'o', label="Gx norm")
plt.plot(WoobyDataFrame["relativeVal_WU"], WoobyDataFrame["myGy"]/max(abs(WoobyDataFrame["myGy"])), 'o', label="Gy norm")
plt.plot(WoobyDataFrame["relativeVal_WU"], WoobyDataFrame["myGz"]/max(abs(WoobyDataFrame["myGz"])), 'o', label="Gz norm")
plt.legend(loc='best')
plt.grid(True)
plt.show()


plt.figure()
plt.plot(WoobyDataFrame["relativeVal_WU"], -WoobyDataFrame["thetadeg"]/max(abs(WoobyDataFrame["thetadeg"])), 'o', label="theta norm")
plt.plot(WoobyDataFrame["relativeVal_WU"], -WoobyDataFrame["phideg"]/max(abs(WoobyDataFrame["phideg"])), 'o', label="phi norm")
plt.legend(loc='best')
plt.grid(True)
plt.show()


