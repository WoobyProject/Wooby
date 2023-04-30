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
# from timeit import default_timer as timer
import time
import matplotlib.pyplot as plt
import math
import json 
from telnetlib import Telnet

import sys
sys.path.append('../pyWooby')
import pyWooby

print("\nCalibration for Wooby\n")

def tare():
    serialPortWooby.write('t'.encode())

##########################        
#    Measurement setup   #
##########################

N_MAX_MEASURES = 700000

REAL_WEIGHT = 1000
# SUBSET = "UNITARY_TEST"
SUBSET = "VccMeasurement" # "Austin"
SUFFIX = "NoWiFI"

SOURCE = "SERIAL" # "TELNET" OR "SERIAL" 


print("Connecting with Wooby via {}...".format(SOURCE))

##########################        
# Serial connexion setup #
##########################

if (SOURCE == "SERIAL"):
    portWooby = '/dev/cu.SLAB_USBtoUART'
    baudRateWooby = 115200;
    
    serialPortWooby = serial.Serial(port = portWooby, baudrate=baudRateWooby,
                               bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE)
    
    serialPortWooby.reset_input_buffer()
    serialPortWooby.reset_output_buffer()
    serialPortWooby.flush()
    
    serialPortWooby.flushInput()
    serialPortWooby.flushOutput()

##########################
# Telnet connexion setup #
##########################

if (SOURCE == "TELNET"):
    
    HOST = "192.168.1.43"
    timeout = 5    # seconds
    
    
    try: tn
    except NameError: 
        tn = Telnet(HOST, 23)
        
    if (tn.eof):
        tn = Telnet(HOST, 23)
        


##########################        
#  Serial data reading   #
##########################


i = 0
WoobyDataFrame = pd.DataFrame()

while (i < N_MAX_MEASURES):
    

    if (SOURCE == "SERIAL"):
        # Serial read section
        tStart = time.time()
        dataLineWoobyRaw =  serialPortWooby.readline()
        tEndMeasure = time.time()
    
        #print("Reading time: {} ms".format((tEndMeasure - tStart)*1000))
        #print("Inwaiting: {} bytes".format(serialPortWooby.inWaiting()))
        #print("Data: {} \n\n".format(dataLineWoobyRaw))
        
        

        if ( (tEndMeasure - tStart) < 10e-3 ):
            print("Emptying the buffer... ")
            continue

        
        try: 
            # dataLineWooby = dataLineWoobyRaw.decode('Ascii')
            dataLineWooby = dataLineWoobyRaw.decode("utf-8")
            
            
        except:
             print("Cannot read line. Skipping... ")
             dataLineWooby = ""
             continue
             
        if (dataLineWooby.startswith('WS')!=True):
            print("Not a complete line or not a measurement line. Skipping... ")
            print(dataLineWooby)
            continue
        
        try:
            dataLineWooby = dataLineWooby[2:-2]
            json_read = json.loads(dataLineWooby)
            df = pd.json_normalize(json_read)
        except:
             print("Unable to convert to JSON. Skipping... ")
             dataLineWooby = ""
             continue
        
    if (SOURCE == "TELNET"):
        tStart = time.time()
        tn_raw = tn.read_until('\n'.encode("ascii"), timeout)
        tEndMeasure = time.time()
       
        if ( (tEndMeasure - tStart) < 0.500 ):
            continue
        
        
        tn_read = tn_raw.decode("utf-8")
        tn_read = tn_read[2:]
        
        try:
            json_read = json.loads(tn_read)
            df = pd.json_normalize(json_read)
        except:
            continue
            # error = error + 1
            print("Error reading line")
            
    
    WoobyDataFrame = WoobyDataFrame.append(df,ignore_index=True)
    tEnd = time.time()
    
    i = i + 1
    print("Line read! ({}/{}) Read time: {:.2f} ms".format(i, N_MAX_MEASURES, (tEndMeasure - tStart)*1000 ))
   

# Closing the serial port would restart the Wooby (not wanted)
# serialPortWooby.close()

print(WoobyDataFrame.head())
print(WoobyDataFrame.keys())

###########################        
#      Calculations       #
###########################

## Adding the real weight
WoobyDataFrame["realWeight"] = [REAL_WEIGHT] * WoobyDataFrame.shape[0]

## Adding time vectors
WoobyDataFrame["timeNorm"] = WoobyDataFrame["tBeforeMeasure"]-WoobyDataFrame["tBeforeMeasure"][0]
WoobyDataFrame["timeMeasure"] = WoobyDataFrame["tAfterMeasure"]-WoobyDataFrame["tBeforeMeasure"]
WoobyDataFrame["timeAlgo"] = WoobyDataFrame["tAfterAlgo"]-WoobyDataFrame["tAfterMeasure"]

WoobyDataFrame["timeSim"] = np.linspace(WoobyDataFrame["timeNorm"][0], WoobyDataFrame["timeNorm"].values[-1], WoobyDataFrame["timeNorm"].shape[0])
# WoobyDataFrame["Te"] =  WoobyDataFrame["timeSim"][1] -  WoobyDataFrame["timeSim"][0]


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
    
    maxTime = np.max(WoobyDataFrame["timeNorm"].append(WoobyDataFrame["timeSim"] ))
    plt.figure()
    plt.plot(WoobyDataFrame["timeNorm"], WoobyDataFrame["timeSim"] )
    plt.plot([0, maxTime], [0, maxTime], '--')
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
    
     
### Algorithm speed performance

    plt.figure()
    plt.plot(WoobyDataFrame["timeNorm"][1:], np.diff(WoobyDataFrame["timeNorm"]) )
    plt.title("Speed per sample analysis")
    plt.ylabel("Speed per sample (ms/sample)")
    plt.xlabel("Time (ms)")
    plt.grid(True)
    
    plt.figure()
    plt.plot(WoobyDataFrame["timeNorm"], WoobyDataFrame["timeMeasure"],  label="Measurement")
    plt.plot(WoobyDataFrame["timeNorm"], WoobyDataFrame["timeAlgo"],     label="Algorithm")
    plt.title("Comparison of the measuremnt time vs. alorigthm exec time")
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



### Filtering analysis (all filters)

    f, (a0, a1) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [3, 1]}, sharex=True)


    a0.plot(WoobyDataFrame["timeNorm"], WoobyDataFrame["relativeVal_WU"]/WoobyDataFrame["calibrationFactor"],          'o-' ,  label="Raw")
    a0.plot(WoobyDataFrame["timeNorm"], WoobyDataFrame["realValue_WU_AngleAdj"]/WoobyDataFrame["calibrationFactor"],   'o--',  label="Angle adj")
    a0.plot(WoobyDataFrame["timeNorm"], WoobyDataFrame["realValue_WU_MovAvg"]/WoobyDataFrame["calibrationFactor"],     'o-' ,  label="Moving avg")
    a0.plot(WoobyDataFrame["timeNorm"], WoobyDataFrame["realValue_WU_Filt"]/WoobyDataFrame["calibrationFactor"],       'o--',  label="Filtered")
    a0.plot(WoobyDataFrame["timeNorm"], WoobyDataFrame["realValue"],                                                   'o--',  label="realValue")
    a0.plot(WoobyDataFrame["timeNorm"], WoobyDataFrame["realValueFiltered"],                                           'o--',  label="realValueFiltered")
    a0.plot(WoobyDataFrame["timeNorm"], WoobyDataFrame["correctedValueFiltered"],                                      'o--',  label="correctedValueFiltered")
    
    a0.grid(True)
    a0.set_title("Correction algorithms analysis")
    a0.set_ylabel("Raw weight values (wu)")
    a0.set_xlabel("Time normalized (ms) ")
    a0.legend(loc="best")

 ## Synchronisation for filtering analysis
    a1.plot(WoobyDataFrame["timeNorm"], WoobyDataFrame["bSync"],          'o-' ,  label="bSync")
    a1.grid(True)
    a1.set_title("Synchronization bool")
    a1.set_ylabel("Synchronization bool")
    a1.set_xlabel("Time normalized (ms) ")
    a1.legend(loc="best")
    
### Final displayed value 
    plt.figure()
    plt.plot(WoobyDataFrame["timeNorm"]/1000, WoobyDataFrame["correctedValueFiltered"], 'o-')
    plt.show()
    plt.grid(True)
    plt.title("Final displayed value")
    plt.ylabel("Raw weight value (wu)")
    plt.xlabel("Time (s)")

 

# Histogram: Weight measurements 
    plt.figure()
    WoobyDataFrameFilt = WoobyDataFrame[(WoobyDataFrame["timeNorm"]>0) & (WoobyDataFrame["timeNorm"]<10000000000000000) ]
    condensed = pd.concat([WoobyDataFrameFilt["relativeVal_WU"], WoobyDataFrameFilt["realValue_WU_AngleAdj"],  
                           WoobyDataFrameFilt["realValue_WU_MovAvg"], WoobyDataFrameFilt["realValue_WU_Filt"]])
                          
    minVal = math.floor(min(condensed)) 
    maxVal = math.ceil(max(condensed))
    bins = np.arange(minVal, maxVal, (maxVal-minVal)/20)
    plt.hist(WoobyDataFrameFilt["relativeVal_WU"],          bins=bins, alpha=0.5, ec='black', label="relativeVal_WU")
    plt.hist(WoobyDataFrameFilt["realValue_WU_AngleAdj"],   bins=bins, alpha=0.5, ec='black', label="realValue_WU_AngleAdj")
    plt.hist(WoobyDataFrameFilt["realValue_WU_MovAvg"],     bins=bins, alpha=0.5, ec='black', label="realValue_WU_MovAvg")
    plt.hist(WoobyDataFrameFilt["realValue_WU_Filt"],       bins=bins, alpha=0.5, ec='black', label="realValue_WU_Filt")
    
    plt.legend(loc='best')
    plt.grid(True)
    plt.show()
    
    print("relativeVal_WU: {:2f}".format(       np.std(WoobyDataFrameFilt["relativeVal_WU"]/WoobyDataFrame["calibrationFactor"])))
    print("realValue_WU_AngleAdj: {:2f}".format(np.std(WoobyDataFrameFilt["realValue_WU_AngleAdj"]/WoobyDataFrame["calibrationFactor"])))
    print("realValue_WU_MovAvg: {:2f}".format(  np.std(WoobyDataFrameFilt["realValue_WU_MovAvg"]/WoobyDataFrame["calibrationFactor"])))
    print("realValue_WU_Filt: {:2f}".format(    np.std(WoobyDataFrameFilt["realValue_WU_Filt"]/WoobyDataFrame["calibrationFactor"])))
    
    print("realValue: {:2f}".format(             np.std(WoobyDataFrameFilt["realValue"])))
    print("realValueFiltered: {:2f}".format(     np.std(WoobyDataFrameFilt["realValueFiltered"])))
    print("correctedValueFiltered: {:2f}".format(np.std(WoobyDataFrameFilt["correctedValueFiltered"])))




### Angles analysis

    # Plot: Angles vs time
    plt.figure()
    plt.plot(WoobyDataFrame["timeNorm"], WoobyDataFrame["thetadeg"], label ="thetadeg")
    plt.plot(WoobyDataFrame["timeNorm"], WoobyDataFrame["phideg"], label ="phideg")
    plt.show()
    plt.grid(True)
    plt.legend(loc='best')
    

### Failures (all filters)

    plt.figure()
    plt.plot(WoobyDataFrame["timeNorm"], WoobyDataFrame["BF_GOOGLE_HTTPREQ"],   'o--',  label="BF_GOOGLE_HTTPREQ")
    plt.plot(WoobyDataFrame["timeNorm"], WoobyDataFrame["BF_SERIALPORT"],       'o--',  label="BF_SERIALPORT")
    plt.plot(WoobyDataFrame["timeNorm"], WoobyDataFrame["BF_SERIALTELNET"],     'o--',  label="BF_SERIALTELNET")
    plt.plot(WoobyDataFrame["timeNorm"], WoobyDataFrame["BF_MPU"],              'o--',  label="BF_MPU")
    plt.plot(WoobyDataFrame["timeNorm"], WoobyDataFrame["BF_WIFI"],             'o--',  label="BF_WIFI")
    plt.show()
    plt.grid(True)
    plt.title("Failure booleans")
    plt.ylabel("Failure booleans")
    plt.xlabel("Time normalized (ms) ")
    plt.legend(loc="best")

## Correction analysis
    
    # Plot: Weight measurements vs time
    plt.figure()
    plt.plot(WoobyDataFrame["timeNorm"], WoobyDataFrame["realValue"],             'o--', label="realValue")
    plt.plot(WoobyDataFrame["timeNorm"], WoobyDataFrame["realValueFiltered"],     'o--', label="realValueFiltered")
    plt.plot(WoobyDataFrame["timeNorm"], WoobyDataFrame["correctedValueFiltered"],'o--', label="correctedValueFiltered")
    plt.legend(loc='best')
    plt.grid(True)
    plt.show()

    # Histogram: Weight measurements 
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


### Vcc analysis
    tout, vccFiltered = pyWooby.filtering.filter_1od(WoobyDataFrame["timeSim"]/1000, WoobyDataFrame["vccVolts"], 10, 0.7)
    ratio = pyWooby.filtering.mapval(vccFiltered, 5.0, 7.4, 0, 1) 
    
    # Plot: Vcc vs time
    plt.figure()
    plt.plot(WoobyDataFrame["timeNorm"]/1000, WoobyDataFrame["vccVolts"], label ="vccVolts")
    plt.plot(tout, vccFiltered, label ="Filtered")
    #plt.plot(tout, ratio*100, label ="Filtered")
    plt.show()
    plt.grid(True)
    plt.legend(loc='best')
    plt.title("Vcc plot")
    plt.ylabel("Vcc (Volts)")
    plt.xlabel("Time normalized (s) ")
    
    # Calculation of the actual ON time
    np.array(WoobyDataFrame[WoobyDataFrame["vccVolts"]>5]["timeNorm"])[-1]/1000/60/60
    
    
    
### Vcc qnqlysis (histogram)
    minVal = math.floor(min(WoobyDataFrame["vccVolts"])) 
    maxVal = math.ceil(max(WoobyDataFrame["vccVolts"]))
    bins = np.linspace(minVal, maxVal, round(math.sqrt(len(WoobyDataFrame["vccVolts"])))  )

    plt.figure()
    plt.hist(WoobyDataFrame["vccVolts"], bins=bins, alpha=0.5, ec='black', label="vccVolts")
    plt.hist(vccFiltered,  bins=bins, alpha=0.5, ec='black', label="Filtered")
    plt.show()
    plt.grid(True)
    plt.legend(loc='best')
    plt.title("Vcc histogram")
    plt.xlabel("Vcc (V) ")
    
    
plt.figure()
plt.plot(WoobyDataFrame["timeNorm"], WoobyDataFrame["realValue_WU"])
plt.show()
plt.grid(True)



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


