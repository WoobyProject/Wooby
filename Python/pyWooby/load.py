import os
import pandas as pd
import re
import numpy as np
import warnings

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
    dataWooby["data"] = extraCalculationWoobyDf(dataWooby["data"])
    return dataWooby


def extraCalculationWoobyDf(data):
    try:
        data["tMeasureRaw"] = data["tAfterMeasure"] - data["tBeforeMeasure"]
    except KeyError:
        warnings.warn("One or more variables required for 'tMeasureRaw' calculation are missing.")
        
    try:
        data["tMeasure"] = data["tAfterAlgo"] - data["tBeforeMeasure"]
    except KeyError:
        warnings.warn("One or more variables required for 'tMeasure' calculation are missing.")
    
    try:
        data["relativeValue_WU"] = data["realValue_WU"] - data["OFFSET"]
    except KeyError:
        warnings.warn("One or more variables required for 'relativeValue_WU' calculation are missing.")
    
    try:
        timeSim = np.linspace(data["timeNorm"][0], data["timeNorm"][-1], len(data["timeNorm"]))
        data["timeSim"] = timeSim
        data["Te"] = timeSim[1] - timeSim[0]
    except KeyError:
        warnings.warn("One or more variables required for 'timeSim' or 'Te' calculation are missing.")
    
    # New variables
    for var in ["tBeforeMeasure1", "tBeforeMeasure2", "tBeforeMeasure3", "tBeforeMeasure4"]:
        try:
            data[f"{var}Norm"] = data[var] - data[var].iloc[0]
        except KeyError:
            warnings.warn(f"Variable '{var}' is missing.")
    
    for var in ["tAfterMeasure1", "tAfterMeasure2", "tAfterMeasure3", "tAfterMeasure4"]:
        try:
            data[f"{var}Norm"] = data[var] - data[var].iloc[0]
        except KeyError:
            warnings.warn(f"Variable '{var}' is missing.")
    
    return data

##########################        
#     Import functions   #
##########################

def importCSV(fileName, fileFolder):
    return pd.read_csv(os.path.join(fileFolder, fileName))
    
def importCSVbatch(fileName, fileFolder):
    if type(fileName) == list :
        results = list()
        for file in fileName:
            results.append(importCSV(file, fileFolder))
        return results
    
    else:
        return None
    