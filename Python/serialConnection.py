#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  6 19:10:16 2020

@author: enriquem
"""

import serial
import timeit


portWooby = '/dev/cu.SLAB_USBtoUART'
baudRateWooby = 9600;

serialPortWooby = serial.Serial(port = portWooby, baudrate=baudRateWooby,
                           bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE)


serialPortWooby.flush()

print(serialPortWooby.in_waiting)
print(serialPortWooby.out_waiting)

# Emptying old data
while ( (tEnd - tStart)*1000 < 500 ) :
    tStart = timer()
    serialPortWooby.readline()
    tEnd = timer()
    
    
N_MAX_MEASURES = 1000

i = 0

while i < N_MAX_MEASURES:
    
    start = timer()
    line = serialPortWooby.readline()
    # print()
    end = timer()
    print("Measurement: {}\tReading time: {} ms".format(i, (end - start)*1000))
    i = i + 1