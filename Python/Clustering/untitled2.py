
import sys
import os
pyWoobyPath =  os.path.join(os.path.split(os.getcwd())[0])
sys.path.append(pyWoobyPath)


from pyWooby import Wooby


## Initializing the Wooby element
myWooby = Wooby()


## Checking available serial ports
avlbSerPorts= myWooby.availableSerialPorts()
print(avlbSerPorts)


## Select the serial port 
port = "/dev/" +  avlbSerPorts[1]
 

## Setup serial connection 
myWooby.setupSerial(port, baudrate = 115200)

WoobyDataFrame = myWooby.read("SERIAL")
WoobyDataFrame = myWooby.readNTimes("SERIAL", 200)


## Completing calculations
WoobyDataFrame = myWooby.extraCalcWooby(WoobyDataFrame)


## Export 
fileFolder = "/Users/enriquem/Documents/HumanityLab/Wooby/Github/Python/datasets/CLUSTERING"
fileName = "Clustering_1.txt"

myWooby.exportCSV(WoobyDataFrame, fileName, fileFolder, overwrite=False)
    


###############################

