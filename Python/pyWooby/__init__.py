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


import signal

from sklearn.linear_model import LinearRegression


def keyboardInterruptHandler(signal, frame):
    print("KeyboardInterrupt (ID: {}) has been caught. Cleaning up...".format(signal))
    exit(0)

signal.signal(signal.SIGINT, keyboardInterruptHandler)

    
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
#    General functions   #
##########################

    def availablePorts(self):
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            ports = []
            raise EnvironmentError('Unsupported platform')
        return ports
        
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
        if ( (tEndMeasure - tStart) < 500e-3 ):
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
            """
            WoobyDataFrame["timeNorm"] =    WoobyDataFrame["tBeforeMeasure"]-WoobyDataFrame["tBeforeMeasure"][0]
            
            WoobyDataFrame["timeMeasure"] = WoobyDataFrame["tAfterMeasure"] - WoobyDataFrame["tBeforeMeasure"]
            WoobyDataFrame["timeAlgo"] =    WoobyDataFrame["tAfterAlgo"]    - WoobyDataFrame["tAfterMeasure"]
            WoobyDataFrame["timeTotal"] =   WoobyDataFrame["tAfterAlgo"]    - WoobyDataFrame["tBeforeMeasure"]
            WoobyDataFrame["timeSim"] =     np.linspace(WoobyDataFrame["timeNorm"][0], WoobyDataFrame["timeNorm"].values[-1], WoobyDataFrame["timeNorm"].shape[0])
            """
            
            if "tBeforeMeasure" in WoobyDataFrame and "tAfterMeasure" in WoobyDataFrame and "tAfterMeasure" in WoobyDataFrame :
                WoobyDataFrame["timeNorm"] = WoobyDataFrame["tBeforeMeasure"] - WoobyDataFrame["tBeforeMeasure"][0]
                WoobyDataFrame["timeMeasure"] = WoobyDataFrame["tAfterMeasure"] - WoobyDataFrame["tBeforeMeasure"]
                WoobyDataFrame["timeAlgo"] = WoobyDataFrame["tAfterAlgo"] - WoobyDataFrame["tAfterMeasure"]
                WoobyDataFrame["timeTotal"] = WoobyDataFrame["tAfterAlgo"] - WoobyDataFrame["tBeforeMeasure"]
                WoobyDataFrame["timeSim"] = np.linspace(WoobyDataFrame["timeNorm"][0], WoobyDataFrame["timeNorm"].values[-1], WoobyDataFrame["timeNorm"].shape[0])
            else:
                for i in range(1, 5):
                    before_measure_key = f"tBeforeMeasure{i}"
                    after_measure_key = f"tAfterMeasure{i}"
                    after_algo_key = f"tAfterAlgo{i}"
                    if before_measure_key in WoobyDataFrame and after_measure_key in WoobyDataFrame and after_algo_key in WoobyDataFrame:
                        WoobyDataFrame[f"timeNorm{i}"] = WoobyDataFrame[before_measure_key] - WoobyDataFrame[before_measure_key][0]
                        WoobyDataFrame[f"timeMeasure{i}"] = WoobyDataFrame[after_measure_key] - WoobyDataFrame[before_measure_key]
                        WoobyDataFrame[f"timeAlgo{i}"] = WoobyDataFrame[after_algo_key] - WoobyDataFrame[after_measure_key]
                        WoobyDataFrame[f"timeTotal{i}"] = WoobyDataFrame[after_algo_key] - WoobyDataFrame[before_measure_key]
                        WoobyDataFrame[f"timeSim{i}"] = np.linspace(WoobyDataFrame[f"timeNorm{i}"][0], WoobyDataFrame[f"timeNorm{i}"].values[-1], WoobyDataFrame[f"timeNorm{i}"].shape[0])
                        
            return WoobyDataFrame
        except Exception as e:
            print("ERROR => {}: {}".format(type(e).__name__, str(e)))
            return None

    def closeSerial(self):
        if ( self.serialPortWooby):
            self.serialPortWooby.close()
        

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
#     Import functions   #
##########################

    def importCSV_(self, fileName, fileFolder):
        return pd.read_csv(os.path.join(fileFolder, fileName))
        
    def importCSVbatch_(self, fileName, fileFolder):
        if type(fileName) == list :
            results = list()
            for file in fileName:
                results.append(self.importCSV(file, fileFolder))
            return results
        
        else:
            return None
        
    def process_file(self, filePath):
        json_objects = []
        
        with open(filePath, 'r') as file:
            for line in file:
                # Remove "WS" from the beginning of each line and strip whitespace
                cleaned_line = line.lstrip('WS').strip()
                if cleaned_line:
                    try:
                        # Attempt to parse the cleaned line as JSON
                        json_object = json.loads(cleaned_line)
                        json_objects.append(json_object)
                    except json.JSONDecodeError as e:
                        print(f"Error decoding line: {cleaned_line}. Error: {e}")
    
        # Convert JSON objects to DataFrame
        df = pd.DataFrame(json_objects)
        return df

            
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
        ## TODO ! This is not reallt working well
        except KeyboardInterrupt:
            return WoobyDataFrame
        except Exception as e:
                print (str(e) )
                if "'exit'" in str(e):
                    
                    print( "WARNING: reading stopped before end with 'KeyboardInterrupt'" )
                    return WoobyDataFrame
                else:
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
        
                 

##################################     
#           Calibration          #
################################## 

    def basicCalibration(self, WoobyDataFrame, verbose=False):
        X = np.array(WoobyDataFrame["realValue_WU"]) #  relativeValue_WU
        y = np.array(WoobyDataFrame["realWeight"])
        
        X = X.reshape((-1, 1))
        y = y.reshape((-1, 1))
        
        reg = LinearRegression().fit(X, y)
        
        # The coefficients & interception
        coeffsreg = reg.coef_
        intercept = reg.intercept_
        
        SLOPE_basic = 1/coeffsreg[0][0]
        
        if (verbose):
            print('\n')
            print('Coefficients: \n',   coeffsreg)
            print('Intercept: \n',      intercept)
            print('\n')
            
            print("\n\nVariable to code as 'calibration_factor': {}\n\n".format(SLOPE_basic))
        
        return reg
    

    