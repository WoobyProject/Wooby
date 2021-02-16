#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 22:40:17 2021

@author: enriquem
"""


import bluetooth

nearby_devices = bluetooth.discover_devices(lookup_names=True)
print("Found {} devices.".format(len(nearby_devices)))

for addr, name in nearby_devices:
    print("  {} - {}".format(addr, name))
    
    

    
    
s = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

hostMACAddress = '24:0A:C4:5F:DF:F2' # The MAC address of a Bluetooth adapter on the server. The server might have multiple Bluetooth adapters. 
port = 0
backlog = 1
size = 1024


s.bind((hostMACAddress, port))
s.listen(backlog)

