import os
import pandas as pd
import re

def readWoobyFile(fileFolder, fileName, verbose=False):
    try:
        fileFullPath = os.path.join(fileFolder, fileName)
        if os.path.isfile(fileFullPath):
            if (".txt" in fileName) or (".csv" in fileName) :
                fileDf = pd.read_csv(fileFullPath)
                print("File read: {}".format(fileName)) if verbose==True else None
                return {"name":fileName, "data":fileDf}
        else:
            print("File do not exist: {}".format(fileName))  if verbose==True else None
            return None
    except:
        print("File read: {}".format(fileName))
        return None

def readWoobyFolder(fileFolder, fileFilter, verbose=False):
    listFinal = []
    allFiles = os.listdir(fileFolder)
    print("{} files found".format(len(allFiles)))  if verbose==True else None
    for fileName in allFiles:
        answer = re.search(fileFilter, fileName)
        if (answer!=None):
            result = readWoobyFile(fileFolder, fileName, verbose=verbose)
            if(result!=None):
                listFinal.append(result)
    return listFinal


def extraCalculationWooby(dataWooby):
    dataWooby["data"]["tMeasureRaw"] =          dataWooby["data"]["tAfterMeasure"] - dataWooby["data"]["tBeforeMeasure"] 
    dataWooby["data"]["tMeasure"] =             dataWooby["data"]["tAfterAlgo"] - dataWooby["data"]["tBeforeMeasure"]
    
    dataWooby["data"]["relativeValue_WU"] =     dataWooby["data"]["realValue_WU"] - dataWooby["data"]["OFFSET"]
    
    return dataWooby