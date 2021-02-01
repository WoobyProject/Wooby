from pyWooby.load import readWoobyFile, readWoobyFolder, extraCalculationWooby
from pyWooby.plot import plotcorrectedWeight
from pyWooby.filtering import genericFilter, filter_1od, movingAvg, myFFT


    
import os
import sys
import glob

from telnetlib import Telnet
import serial

import pandas as pd 
import numpy as np

import time
import json

class Wooby():
    
    serialPortWooby = None
    telnetPortWooby = None
    DataList = []
    nMaxMeasures = 10000
    
    def __init__(self):
        #print("Creation of a pyWooby instance")
        self.serialPortWooby = None
        self.telnetPortWooby = None
        

##########################        
#     Telnet functions   #
##########################

    
    def setupTelnet(self, HOST, timeout=5, port=23):
        
        #timeout is in seconds
        try:
            self.telnetPortWooby = Telnet(HOST, port)
            self.TelnetTimeout = timeout
            return True
        except:
            self.telnetPortWooby = None
            return False
         
    def telnetRead(self):
        tStart = time.time()
        tn_raw = self.telnetPortWooby.read_until('\n'.encode("ascii"), self.TelnetTimeout )
        tEndMeasure = time.time()
       
        if ( (tEndMeasure - tStart) < 0.500 ):
            return None
        
        tn_read = tn_raw.decode("utf-8")
        tn_read = tn_read[2:]
        
        try:
            json_read = json.loads(tn_read)
            df = pd.json_normalize(json_read)
            return df
        except:
            return None
            # error = error + 1
            print("Error reading line")

##########################        
#     Tare functions     #
##########################

    def serialTare(self):
        try:
            self.serialPortWooby.write('t'.encode())
        except:
            print("ERROR: not possible to tare with Serial Comm")
    
    def tare(self):
        self.serialTare()

##########################
#     Serial functions   #
##########################
        
    def setupSerial(self, port, baudrate = 115200):
        ##########################        
        # Serial connexion setup #
        ##########################
            
        try:
            self.serialPortWooby = serial.Serial(port = port, baudrate=baudrate,
                                       bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE)
            
            self.serialPortWooby.reset_input_buffer()
            self.serialPortWooby.reset_output_buffer()
            self.serialPortWooby.flush()
            
            self.serialPortWooby.flushInput()
            self.serialPortWooby.flushOutput()
            
            return True
        except Exception as e:
            print("ERROR => {}: {}".format(type(e).__name__, str(e)))
            return False

    def availableSerialPorts(self):
        
        return [x.name for x in serial.tools.list_ports.comports() ]
    
    def serialRead(self):
        
        # Serial read section
        tStart = time.time()
        dataLineWoobyRaw =  self.serialPortWooby.readline()
        tEndMeasure = time.time()
    
        #print("Reading time: {} ms".format((tEndMeasure - tStart)*1000))
        #print("Inwaiting: {} bytes".format(serialPortWooby.inWaiting()))
        #print("Raw data: {} \n\n".format(dataLineWoobyRaw))
        
        # Emptying the buffer
        if ( (tEndMeasure - tStart) < 100e-3 ):
            print("Emptying the buffer... ")
            return None

        # Actual reading
        try: 
            dataLineWooby = dataLineWoobyRaw.decode("utf-8")
        except:
             print("Cannot read line. Skipping... ")
             dataLineWooby = ""
             return None
             
        # Verifying if it's a Serial line with info
        if (dataLineWooby.startswith('WS')!=True):
            print("Not a complete line or not a measurement line. Skipping... ")
            print("Data line:{}".format(dataLineWooby))
            return None
        
        # Transforming into JSON and DataFrame
        try:
            dataLineWoobyJS = dataLineWooby[2:]
            json_read = json.loads(dataLineWoobyJS)
            df = pd.json_normalize(json_read)
            return df
        except:
            print("Unable to convert to JSON. Skipping... ")
            print("Data line:{}".format(dataLineWooby))
            dataLineWooby = ""
            return None

    def extraCalcWooby(self, WoobyDataFrame):
        
        try:
            
            WoobyDataFrame["timeNorm"] =    WoobyDataFrame["tBeforeMeasure"]-WoobyDataFrame["tBeforeMeasure"][0]
            
            WoobyDataFrame["timeMeasure"] = WoobyDataFrame["tAfterMeasure"] - WoobyDataFrame["tBeforeMeasure"]
            WoobyDataFrame["timeAlgo"] =    WoobyDataFrame["tAfterAlgo"]    - WoobyDataFrame["tAfterMeasure"]
            WoobyDataFrame["timeTotal"] =   WoobyDataFrame["tAfterAlgo"]    - WoobyDataFrame["tBeforeMeasure"]
            WoobyDataFrame["timeSim"] =     np.linspace(WoobyDataFrame["timeNorm"][0], WoobyDataFrame["timeNorm"].values[-1], WoobyDataFrame["timeNorm"].shape[0])
    
            return WoobyDataFrame
        except Exception as e:
            print("ERROR => {}: {}".format(type(e).__name__, str(e)))
            return None

##########################        
#     Export functions   #
##########################  
          
    def exportCSV(self, WoobyDataFrame, fileName, fileFolder, overwrite=False):
        
        if (WoobyDataFrame is None):
            print("Data frame is none")
            return
        
        fileFullPath = os.path.join(fileFolder, fileName)
        
        # Check if the folder exists (if not it is created)
        if os.path.isdir(fileFolder) == False :
            os.mkdir(fileFolder)
        
        # Check if the file exists
        if os.path.isfile(fileFullPath):
            print("File already exists")
            if (overwrite):
                print("Overwriting...")
                fileWooby = open(fileFullPath, "w")
                fileWooby.write(WoobyDataFrame.to_csv(index=False))
                fileWooby.close()
        else:
            fileWooby = open(fileFullPath, "w")
            fileWooby.write(WoobyDataFrame.to_csv(index=False))
            fileWooby.close()



##########################        
#    Reading functions   #
##########################
    
    
    def read(self, commType):
        # Reads only one valid point
        
        if (commType == "SERIAL"):
           return self.serialRead()
            
        if (commType == "TELNET"):
           return self.telnetRead()            
    
    
    def readNTimes(self, commType, nMeasures):
        # Reads N valid points
        
        # Initial variables
        WoobyDataFrame = pd.DataFrame()
        i = 0
        
        try:
            while (i < nMeasures):
                tStart = time.time()
                
                df = self.read(commType)
               
                if (df is None):
                    print("Empty line ...")
                else:
                    WoobyDataFrame = WoobyDataFrame.append(df,ignore_index=True)
                    tEnd = time.time()
                    i = i + 1
                    print("Line read! ({}/{}) Read time: {:.2f} ms".format(i, nMeasures, (tEnd - tStart)*1000 ))
       
            return WoobyDataFrame
            
        except Exception as e:
            print("ERROR: reading line in readNTimes()")
            print("{}: {}".format(type(e).__name__, str(e)))
                   
    def readUntil(self, commType):
        # Reading until the function sis stopped
        # However the library sets a maximum of read valid points 
        
        return self.readNTimes(commType, self.nMaxMeasures)
       
   
    def appendCalibPoint(self, WoobyDataFrame):
        try:
            if (WoobyDataFrame is None):
                raise Exception("WoobyDataFrame is 'None'")
                
            self.DataList.append(WoobyDataFrame)
            return True
        except Exception as e:
            print("ERROR => {}: {}".format(type(e).__name__, str(e)))
            return False
            
        
    def readCalibPoint(self, subset, suffix, realWeight, commType, nMeasures, fileName, fileFolder, overwrite=False):
        WoobyDataFrame = self.readNTimes(commType, nMeasures)
        WoobyDataFrame = self.extraCalcWooby(WoobyDataFrame)
        WoobyDataFrame["realWeight"] = [realWeight] * WoobyDataFrame.shape[0]

        if not (WoobyDataFrame is None):
            self.appendCalibPoint(WoobyDataFrame)
            self.exportCSV(WoobyDataFrame, fileName, fileFolder, overwrite)
        
                 


    