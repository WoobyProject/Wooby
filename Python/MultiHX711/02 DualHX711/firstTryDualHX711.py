#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 12 18:36:30 2021

@author: enriquem
"""


import sys
import os


maindir = os.path.dirname(__file__)
print(maindir)

maindir = "/Users/enriquem/Documents/HumanityLab/Wooby/GitHub2Test/Wooby/Python/"
pckgdir = os.path.realpath(os.path.join(maindir, "pyWooby"))
sys.path.append(maindir)
print(pckgdir)

from pyWooby import Wooby


myWooby = Wooby()

myWooby.availablePorts()

# %% 

portWooby =  '/dev/tty.usbserial-0001' # '/dev/cu.SLAB_USBtoUART'


baudRateWooby = 115200;
    
myWooby.setupSerial(portWooby, baudRateWooby)

# %%

myWooby.tare()

dfDualLoadCell = myWooby.readUntil("SERIAL")


# %%

import matplotlib.pyplot as plt

dfDualLoadCell.keys()

# dfDualLoadCell["BF_MPU"]


# Plot of two sensors - raw data !
plt.figure()
plt.plot(dfDualLoadCell["tBeforeMeasure1"] ,  dfDualLoadCell["realValue_WU1"] , label="Sensor 1")
plt.plot(dfDualLoadCell["tBeforeMeasure2"] ,  dfDualLoadCell["realValue_WU2"] , label="Sensor 2")
plt.grid(True)
plt.legend()
plt.show()

# Plot of two sensors -  with the offset normalization
plt.figure()
plt.plot(dfDualLoadCell["tBeforeMeasure1"] ,  dfDualLoadCell["relativeVal_WU1"] , label="Sensor 1")
plt.plot(dfDualLoadCell["tBeforeMeasure2"] ,  dfDualLoadCell["relativeVal_WU2"] , label="Sensor 2")
plt.grid(True)
plt.legend()
plt.show()


# Plot of offset
plt.figure()
plt.plot(dfDualLoadCell["tBeforeMeasure1"] ,  dfDualLoadCell["offset1"], label="Sensor 1")
# plt.plot(dfDualLoadCell["tBeforeMeasure1"] ,  dfDualLoadCell["relativeVal_WU1"], '--' , label="Sensor 1 relative")
plt.plot(dfDualLoadCell["tBeforeMeasure2"] ,  dfDualLoadCell["offset2"], label="Sensor 2")
plt.grid(True)
plt.legend()
plt.show()

# Mult of two 
plt.figure()
plt.plot(dfDualLoadCell["tBeforeMeasure1"] ,  (dfDualLoadCell["realValue_WU1"] - dfDualLoadCell["realValue_WU1"][0] ) * ( dfDualLoadCell["realValue_WU2"] - dfDualLoadCell["realValue_WU2"][0]), label="Sum")
# plt.plot(dfDualLoadCell["tBeforeMeasure1"] ,  dfDualLoadCell["relativeVal_WU1"], '--' , label="Sensor 1 relative")
plt.grid(True)
plt.legend()
plt.show()


# Sum of two 
plt.figure()
plt.plot(dfDualLoadCell["tBeforeMeasure1"] ,  dfDualLoadCell["realValue_WU1"] - dfDualLoadCell["realValue_WU1"][0] + dfDualLoadCell["realValue_WU2"] - dfDualLoadCell["realValue_WU2"][0], label="Sum")
# plt.plot(dfDualLoadCell["tBeforeMeasure1"] ,  dfDualLoadCell["relativeVal_WU1"], '--' , label="Sensor 1 relative")
plt.grid(True)
plt.legend()
plt.show()


calib_factor = 2000/94000

# Plot of two sensors IN GR ! -  with offset normalization
plt.figure()
plt.plot(dfDualLoadCell["tBeforeMeasure1"] ,  calib_factor*(dfDualLoadCell["realValue_WU1"] - dfDualLoadCell["offset1"]), label="Sensor 1")
# plt.plot(dfDualLoadCell["tBeforeMeasure1"] ,  dfDualLoadCell["relativeVal_WU1"], '--' , label="Sensor 1 relative")
plt.plot(dfDualLoadCell["tBeforeMeasure2"] ,  calib_factor*(dfDualLoadCell["realValue_WU2"] - dfDualLoadCell["offset2"]), label="Sensor 2")
plt.grid(True)
plt.legend()
plt.show()


# Sum of two IN GR !
plt.figure()
plt.plot(dfDualLoadCell["tBeforeMeasure1"] ,  calib_factor*( dfDualLoadCell["realValue_WU1"] - dfDualLoadCell["realValue_WU1"][0] + dfDualLoadCell["realValue_WU2"] - dfDualLoadCell["realValue_WU2"][0] ), label="Sum")
# plt.plot(dfDualLoadCell["tBeforeMeasure1"] ,  dfDualLoadCell["relativeVal_WU1"], '--' , label="Sensor 1 relative")
plt.grid(True)
plt.legend()
plt.show()


#%% 
plt.figure()
"""
plt.plot(dfDualLoadCell["relativeVal_WU1"] ,  dfDualLoadCell["myAx"], marker='o', linestyle='None', label="Ax" )
plt.plot(dfDualLoadCell["relativeVal_WU1"] ,  dfDualLoadCell["myAy"], marker='o', linestyle='None', label="Ay" )
plt.plot(dfDualLoadCell["relativeVal_WU1"] ,  dfDualLoadCell["myAz"], marker='o', linestyle='None', label="Az" )
"""
# plt.plot(dfDualLoadCell["relativeVal_WU2"] ,  dfDualLoadCell["myAx"], marker='o', linestyle='None', label="Ax" )
# plt.plot(dfDualLoadCell["relativeVal_WU2"] ,  dfDualLoadCell["myAy"], marker='o', linestyle='None', label="Ay" )
#plt.plot(dfCorr["relativeVal_WU1"] ,  dfCorr["deltaAx"], marker='o', linestyle='None', label="Ax" )
plt.scatter(dfCorr["relativeVal_WU1"] ,  dfCorr["deltaAx"], c=dfCorr["deltaAz"], marker='o', linestyle='None', label="Ax" )

plt.grid(True)
plt.legend()
plt.show()

dfCorr = dfDualLoadCell.copy()

dfCorr["deltaAx"] = dfCorr["myAx"]- dfCorr["myAx"][0]
dfCorr["deltaAy"] = dfCorr["myAy"]- dfCorr["myAy"][0]
dfCorr["deltaAz"] = dfCorr["myAz"]- dfCorr["myAz"][0]

dfCorr[ ["relativeVal_WU1", "deltaAx", "deltaAy", "deltaAz"] ].corr()


dfDualLoadCell[ ["relativeVal_WU1", "myAx", "myAy", "myAz"] ].corr()

plt.figure()
plt.plot(dfDualLoadCell["tBeforeMeasure1"] ,  dfDualLoadCell["myAx"], label="Ax" )
plt.plot(dfDualLoadCell["tBeforeMeasure1"] ,  dfDualLoadCell["myAy"], label="Ay" )
plt.plot(dfDualLoadCell["tBeforeMeasure1"] ,  dfDualLoadCell["myAz"], label="Az" )
plt.grid(True)
plt.legend()
plt.show()


# %% 


plt.figure()
plt.plot(dfDualLoadCell["tBeforeMeasure1"] ,  dfDualLoadCell["tBeforeMeasure1"], '--' )
plt.plot(dfDualLoadCell["tBeforeMeasure1"] ,  dfDualLoadCell["tBeforeMeasure2"] )
plt.grid(True)
plt.legend()
plt.show()




plt.figure()
plt.plot(dfDualLoadCell["tBeforeMeasure1"] ,  dfDualLoadCell["thetadeg"], label="theta" )
plt.plot(dfDualLoadCell["tBeforeMeasure1"] ,  dfDualLoadCell["phideg"], label="phi" )
plt.grid(True)
plt.legend()
plt.show()
