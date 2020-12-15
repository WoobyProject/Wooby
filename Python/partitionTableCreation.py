#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  8 12:12:01 2020

@author: enriquem
"""

"""
# Name,   Type, SubType, Offset,  Size, Flags
nvs,      data, nvs,     0x9000,  0x5000,
otadata,  data, ota,     0xe000,  0x2000,
app0,     app,  ota_0,   0x10000, 0x140000,
app1,     app,  ota_1,   0x150000,0x140000,
spiffs,   data, spiffs,  0x290000,0x170000,

"""

myList = ["0x5000", "0x2000", "0x140000", "0x140000", "0x170000"]

sm = 0 
for s in myList:
    d = int(s, 16)
    print(d)
    sm = sm +d

print("\nTotal size: {}\n".format(sm/1e6))


upsize = 0x30000

newSizes = [int(x,16) for x in myList]
newSizes[2] = newSizes[2] + upsize
newSizes[3] = newSizes[3] + upsize
newSizes[4] = newSizes[4] - 2*upsize

init_offset = int("0x9000", 16)
offset = init_offset
newsum = 0
for ns in newSizes:
    
    print("{}, {}".format(hex(offset), hex(int(ns))))
    offset = offset + int(ns)
    newsum = newsum + int(ns)


print("\nTotal new size: {}\n".format(newsum/1e6))