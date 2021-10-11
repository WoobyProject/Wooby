#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  2 23:22:58 2020

@author: enriquem
"""

import sys
import os


maindir = os.path.dirname(__file__)
print(maindir)
pckgdir = os.path.realpath(os.path.join(maindir, "pyWooby"))
sys.path.append(maindir)
print(pckgdir)

from pyWooby import Wooby

#%% Creation of the Serial communication


myWooby = Wooby()

portWooby = '/dev/cu.SLAB_USBtoUART'
baudRateWooby = 115200;
    
myWooby.setupSerial(portWooby, baudRateWooby)




#%% Reading of a calibration point

# print(myWooby.readUntil("SERIAL"))
# myWooby.readNTimes("SERIAL", 10)

N_MAX_MEASURES = 100
REAL_WEIGHT = 2000
SUBSET = "Wooby1" 
SUFFIX = "2"
SOURCE = "SERIAL" # "TELNET" OR "SERIAL" 
FILE_NAME = "{}_{}gr_{}.txt".format(SUBSET, REAL_WEIGHT, SUFFIX)
FILE_FOLDER = os.path.join("/Users/macretina/Documents/Humanity Lab/Wooby/Github/Python/datasets", SUBSET)
OVERWRITE = True

myWooby.readCalibPoint(SUBSET, SUFFIX, REAL_WEIGHT, SOURCE, N_MAX_MEASURES, FILE_NAME, FILE_FOLDER, OVERWRITE)

print(myWooby.DataList[-1])


