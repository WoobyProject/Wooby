#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 16 13:35:07 2021

@author: enriquem
"""

fileHtml = open("/Users/enriquem/Documents/HumanityLab/Wooby/Github/ESP32/html/testWoobyPage.html", "r")
fileExport = open("/Users/enriquem/Documents/HumanityLab/Wooby/Github/ESP32/html/newTestWoobyPage.html", "w")

fileExport.truncate(0)

lines = fileHtml.readlines()
print(lines)

for line in lines:
    newLine  = "\"" + lines[2] +  "\"" 
    print(newLine)
    fileExport.write(newLine)


fileHtml.close()
fileExport.close()
