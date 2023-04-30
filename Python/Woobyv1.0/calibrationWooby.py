#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 00:41:26 2020

@author: enriquem
"""

import re
import os
import pandas as pd
import numpy as np
import seaborn as sns

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter

from sklearn.linear_model import LinearRegression

plt.close('all')


import sys
sys.path.append('../pyWooby')
import pyWooby


##################################        
#       Reading of each file     #
##################################

# Configuration
filterStr_Basic = 'FLAT'
filterStr_Adv = '' #'FLAT'
filterStr_OutOfDom = "FRONT|BACK"

fileFolder = os.path.join(os.getcwd(), "datasets", "WOOBY2_CALIB_BOTTOM")
fileFolder = "/Users/enriquem/Documents/HumanityLab/Wooby/GitHub3/Wooby/Python/datasets/WoobyTripleHX711"
allFiles = os.listdir(fileFolder)

print("Calibration will be done with files in {}... \n".format(fileFolder))

listFiles_Basic = []
listFiles_Adv = []
listFiles_OutOfDom = []

mainWoobyDF_Basic = pd.DataFrame()
mainWoobyDF_Adv = pd.DataFrame()
mainWoobyDF_OutOfDom = pd.DataFrame()

for file in allFiles:
    
    # Getting the weight
    actualWeightStr = re.search('[\d]*gr', file)
    if (actualWeightStr!=None):
        ACTUAL_WEIGHT = float(actualWeightStr.group()[:-2])
        print("File found: {}\t Weight: {}".format(file, ACTUAL_WEIGHT))
        
        # Reading
        fileDf = pd.read_csv(os.path.join(fileFolder, file))
        # Extra calcuations
        fileDf["relativeValue_WU"] = fileDf["realValue_WU"]- fileDf["OFFSET"]
        fileDf["relativeValue_WU_0"] = max(fileDf["relativeValue_WU"])
        
        # Filtering
        answerStr_Basic = re.search(filterStr_Basic, file)
        if (answerStr_Basic!=None):
            mainWoobyDF_Basic = mainWoobyDF_Basic.append(fileDf)
            listFiles_Basic.append({"name":file, 
                                    "data":fileDf})
            
        answerStr_Adv = re.search(filterStr_Adv, file)
        if (answerStr_Adv!=None):
            mainWoobyDF_Adv = mainWoobyDF_Adv.append(fileDf)
            listFiles_Adv.append({"name":file, 
                                  "data":fileDf})
        
        answerStr_OutOfDom = re.search(filterStr_OutOfDom, file)
        if (answerStr_OutOfDom!=None):
            mainWoobyDF_OutOfDom = mainWoobyDF_OutOfDom.append(fileDf)
            listFiles_OutOfDom.append({"name":file, 
                                       "data":fileDf})
        

##################################     
#          Calculations          #
################################## 

mainWoobyDF_Adv["absThetadeg"] = abs(mainWoobyDF_Adv["thetadeg"])
mainWoobyDF_Adv["absPhideg"] = abs(mainWoobyDF_Adv["phideg"])

##################################     
#    Linear regression (basic)   #
################################## 

X = np.array(mainWoobyDF_Basic["relativeValue_WU"])
y = np.array(mainWoobyDF_Basic["realWeight"])

X = X.reshape((-1, 1))
y = y.reshape((-1, 1))

reg = LinearRegression().fit(X, y)

# The coefficients & interception
coeffsreg = reg.coef_
intercept = reg.intercept_

print('\n')
print('Coefficients: \n',   coeffsreg)
print('Intercept: \n',      intercept)
print('\n')

SLOPE_basic = 1/coeffsreg[0][0]

print("\n\nVariable to code as 'calibration_factor': {}\n\n".format(SLOPE_basic))

##################################     
#      Tendency line (basic)     #
################################## 

X_tend_line = np.array([ min(X)[0], max(X)[0]]).reshape((-1, 1))
y_tend_line = reg.predict(X_tend_line)

##################################     
#        Plotting of data        #
################################## 

plt.figure()

'''
for file in listFiles:
    #plt.plot(file["realValue_WU"],  file["realWeight"], 'ro')
    plt.plot(file["relativeValue_WU"],  file["realWeight"], 'ro')
'''
plt.plot(X, y, 'ro')
# Tendency line (basic)
plt.plot(X_tend_line, y_tend_line)

plt.xlabel('Relative measured weight (bits)')
plt.ylabel('Real weight (gr)')
plt.grid(True)
plt.title("Plotting of all the data")
plt.show()

##################################     
#      Predictions (basic)       #
################################## 

y_predOnTrain = reg.predict(X)
identLine = [min(y), max(y)]
MSE = np.square(np.subtract(y_predOnTrain,y)).mean() 

plt.figure()
plt.plot((y_predOnTrain-y), 'o')
#plt.plot(identLine, identLine)
plt.title("Error for the prediction on the training set (MSE={:.2f})".format(MSE))
plt.ylabel("Error (gr)")
plt.xlabel("Measure [n]")
plt.grid(True)
plt.show()

##################################     
#   Linear regression (advance)  #
################################## 

# selected_feat = ["relativeValue_WU" ,"thetadeg", "phideg", "myTmp"]
selected_feat = ["relativeValue_WU" ,"absThetadeg", "absPhideg"]
# selected_feat = ["relativeValue_WU" ,"absThetadeg"]
X_adv = np.array(mainWoobyDF_Adv[selected_feat])
y_adv = np.array(mainWoobyDF_Adv["realWeight"])


y_adv = y_adv.reshape((-1, 1))

reg_adv = LinearRegression().fit(X_adv, y_adv)

# The coefficients & interception
coeffsreg_adv = reg_adv.coef_[0]
intercept_adv = reg_adv.intercept_[0]

print('\n')
print('Coefficients (adv): \n',   coeffsreg_adv)
print('Intercept (adv): \n',      intercept_adv)
print('\n')

SLOPE_adv = 1/coeffsreg_adv[0]

# Variation with the basic calculation
(SLOPE_adv - SLOPE_basic)/SLOPE_basic

for ii in range(0, len(selected_feat)):
    plt.figure()
    plt.plot(X_adv[:,ii], y_adv, 'ro')
    plt.xlabel(selected_feat[ii])
    plt.ylabel("realWeight")
    plt.title("{} vs. real weight".format(selected_feat[ii]))
    plt.grid(True)
    plt.show()


##################################     
#   Plotting of data (advance)   #
################################## 

plt.figure()

'''
for file in listFiles:
    #plt.plot(file["realValue_WU"],  file["realWeight"], 'ro')
    plt.plot(file["relativeValue_WU"],  file["realWeight"], 'ro')
'''
plt.plot(X_adv[:,0], y_adv, 'o')
plt.plot(X, y, 'o')
# Tendency line (basic)
plt.plot(X_tend_line, y_tend_line)

plt.xlabel('Relative measured weight (bits)')
plt.ylabel('Real weight (gr)')
plt.grid(True)
plt.title("Plotting of all the data")
plt.show()



##################################     
#    Predictions (advance)       #
################################## 

y_predOnTrain_adv = reg_adv.predict(X_adv)
identLineAdv = [min(y_adv), max(y_adv)]
MSE_adv = np.square(np.subtract(y_predOnTrain_adv,y_adv)).mean() 

plt.figure()
plt.plot(y_predOnTrain_adv-y_adv, '^')
#plt.plot(identLine, identLine)
plt.title("Error for the prediction on the training set (MSE={:.2f})".format(MSE))
plt.ylabel("Error (gr)")
plt.xlabel("Measure [n]")
plt.grid(True)
plt.show()


plt.figure()
plt.plot(y_predOnTrain_adv, y_predOnTrain_adv, 'o', label = "Prediction")
plt.plot(y_adv, y_adv, 'o', label = "Real weight")
plt.plot(identLineAdv, identLineAdv)
plt.grid(True)
plt.legend(loc='best')
plt.show()



##################################     
#         Theta polyfit          #
################################## 

# Selecting the data
listAux = []

for item1 in listFiles_OutOfDom:
    string1 = item1["name"]
    answer1 = re.search("FRONT", string1)
    if answer1 != None :
        string2 = string1.replace("FRONT", "BACK")
        for item2 in listFiles_OutOfDom:
            answer2 = re.search(string2, item2["name"])
            if answer2 != None :
                print("{} with {}".format( item1["name"],  item2["name"]))
                newDf = {"name":string1.replace("FRONT","MERGED"),
                         "data":item1["data"].append(item2["data"])}
                listAux.append(newDf)
     
            
# Plotting the theta data

listPolyTheta = []
listWeigthAtZero = []
arrayPolyTheta = np.zeros((len(listAux), 3))
plotThetaVsWu = plt.figure()
for i, item in enumerate(listAux):
    
    coeffsTheta = np.polyfit(item["data"]["thetadeg"], item["data"]["relativeValue_WU"], 2)
    arrayPolyTheta[i,:] = coeffsTheta
                  
    p = np.poly1d(coeffsTheta)
                  
    listPolyTheta.append(p)
    listWeigthAtZero.append(p(0))
    
    # plt.plot(item["data"]["thetadeg"], ((item["data"]["relativeValue_WU"]))
             
    plt.plot(item["data"]["thetadeg"], ((item["data"]["relativeValue_WU"])/p(0)) , label=item["data"]["realWeight"].values[0])
    # plt.plot(item["data"]["thetadeg"], ((item["data"]["relativeValue_WU"])/p(0) - 1 - m_a*item["data"]["thetadeg"]**2 )/item["data"]["thetadeg"] , label=item["data"]["realWeight"].values[0])

plt.xlabel("Theta [deg]")
plt.ylabel("Raw weight [bits]")
plt.show()
plt.grid(True)
plt.legend(loc="best")


# Polyfit over theta data (a coeff)
X_a = np.array(listWeigthAtZero)
y_a = np.array(arrayPolyTheta[:, 0])

X_a = X_a.reshape((-1, 1))
y_a = y_a.reshape((-1, 1))


reg_a = LinearRegression().fit(X_a, y_a)
m_a = 1.0*reg_a.coef_[0][0]

print(reg_a.coef_)
print(reg_a.intercept_)


# Polyfit over theta data (b coeff)

X_b = np.array(listWeigthAtZero)
y_b = np.array(arrayPolyTheta[:, 1])

X_b = np.array([0, max(X_b)])
y_b = np.array([0, min(y_b)])

X_b = X_b.reshape((-1, 1))
y_b = y_b.reshape((-1, 1))


reg_b = LinearRegression().fit(X_b, y_b)
m_b = 1.0*reg_b.coef_[0][0]


# Plotting coeffs

X_test = np.array( [min(listWeigthAtZero)*0, max(listWeigthAtZero)] ).reshape((-1, 1))

plt.figure()
plt.plot(listWeigthAtZero, arrayPolyTheta[:, 0], 'o')
plt.title("a coeff")
plt.plot(X_test, reg_a.predict(X_test))


plt.figure()
plt.plot(listWeigthAtZero, arrayPolyTheta[:, 1], 'o')
plt.title("b coeff")
plt.plot(X_test, reg_b.predict(X_test))


plt.figure()
plt.plot(listWeigthAtZero, arrayPolyTheta[:, 2], 'x', ms=10)
plt.title("c coeff")


##################################     
#    Testing of the algorithm    #
################################## 

#m_a = m_a_Xtreme
#m_b = m_b_Xtreme*0


plt.figure()
for i, item in enumerate(listAux):
    
    correctedInThetaVal = item["data"]["relativeValue_WU"]/(1+m_a*(item["data"]["thetadeg"])**2)
    print("Average values (bits): {}({})".format(np.mean(correctedInThetaVal), np.array(item["data"]["realWeight"])[0]))
    print("Average values (gr): {}({})".format(np.mean(correctedInThetaVal)/SLOPE_basic, np.array(item["data"]["realWeight"])[0]))
    print("\n")
    plt.plot(item["data"]["thetadeg"], item["data"]["relativeValue_WU"] , 'o' , label="")
    plt.plot(item["data"]["thetadeg"], correctedInThetaVal , 'k*' )



thetaVec = np.arange(-30, 30, 1)
for W0 in listWeigthAtZero:
    plt.plot( thetaVec, W0*(1+m_a*thetaVec**2) , 'k--')



plt.figure()
for i, item in enumerate(listFiles_Basic):
    plt.scatter(item["data"]["relativeValue_WU"], item["data"]["relativeValue_WU"], label=item["data"]["realWeight"][0])

plt.legend(loc="best")



# Calculations

mainWoobyDF_Basic["correctedRawValue"]  = mainWoobyDF_Basic["realValue_WU"]/(1+m_a*mainWoobyDF_Basic["thetadeg"]**2 +  m_b*mainWoobyDF_Basic["thetadeg"])
mainWoobyDF_Basic["newCorrectedValue"] = (mainWoobyDF_Basic["correctedRawValue"] - mainWoobyDF_Basic["OFFSET"])/SLOPE_basic

               
mainWoobyDF_Adv["correctedRawValue"]  = mainWoobyDF_Adv["realValue_WU"]/(1+m_a*mainWoobyDF_Adv["thetadeg"]**2 +  m_b*mainWoobyDF_Adv["thetadeg"])
mainWoobyDF_Adv["newCorrectedValue"] = (mainWoobyDF_Adv["correctedRawValue"] - mainWoobyDF_Adv["OFFSET"])/SLOPE_basic


for element in listFiles_Adv:
    element["data"]["correctedRawValue"]  = element["data"]["realValue_WU"]/(1 + m_a*element["data"]["thetadeg"]**2 + m_b*element["data"]["thetadeg"])
    element["data"]["newCorrectedValue"] = (element["data"]["correctedRawValue"] - element["data"]["OFFSET"])/SLOPE_basic
    
    
# Plots

'''
plt.figure()
seaborn.scatterplot(mainWoobyDF_Basic["realWeight"], mainWoobyDF_Basic["newCorrectedValue"], 
                    marker='o', c=mainWoobyDF_Basic["thetadeg"], label="basic")
'''
'''
plt.scatter(mainWoobyDF_Adv["realWeight"], mainWoobyDF_Adv["newCorrectedValue"], 
                marker='*', c=mainWoobyDF_Basic["thetadeg"], label="advance")
'''

plt.figure()
plt.scatter(mainWoobyDF_Adv["realWeight"], mainWoobyDF_Adv["correctedValueFiltered"], 
                marker='^', label="before")
plt.scatter(mainWoobyDF_Adv["realWeight"], mainWoobyDF_Adv["newCorrectedValue"], 
                marker='*', label="new")

plt.scatter(mainWoobyDF_Basic["realWeight"], mainWoobyDF_Basic["newCorrectedValue"], 
                marker='o', label="basic")

# print(np.std(mainWoobyDF_Adv["correctedValueFiltered"]))

plt.plot([0, 10000], [0, 10000], 'k--')
plt.legend(loc="best")

b=0
g=0

for element in listFiles_Adv:
    print(element["name"])
    print("Mean dev(normal)= {:.2f} \tMean dev(new)={:.2f}".format(np.mean(element["data"]["correctedValueFiltered"]), 
                                                                   np.mean(element["data"]["newCorrectedValue"]),
                                               ))
    std_old = np.std(element["data"]["correctedValueFiltered"])
    std_new = np.std(element["data"]["newCorrectedValue"])
    print("Std dev(normal)= {:.2f} \tStd dev(new)={:.2f}".format(std_old,std_new))
    if std_old >std_new:
        print("Good!")
        g=g+1
    else:
        print("Bad")
        b=b+1
        
    print("\n")
    
print("g = {}".format(g))
print("b = {}".format(b))
   
plt.figure()
plt.plot(mainWoobyDF_Adv["realValue_WU"], mainWoobyDF_Adv["correctedRawValue"], 'o')
plt.plot([-100000, 400000], [-100000, 400000])
plt.legend(loc="best")

         
##################################     
#            Sandbox             #
################################## 

plt.figure()
plt.scatter(mainWoobyDF_Adv["thetadeg"], mainWoobyDF_Adv["relativeValue_WU"]/SLOPE_basic)
plt.scatter(mainWoobyDF_Basic["thetadeg"], mainWoobyDF_Basic["relativeValue_WU"]/SLOPE_basic)

plt.figure()
plt.scatter(mainWoobyDF_Adv["phideg"], mainWoobyDF_Adv["relativeValue_WU"])
plt.scatter(mainWoobyDF_Basic["phideg"], mainWoobyDF_Basic["relativeValue_WU"])

plt.figure()
plt.scatter(mainWoobyDF_Adv["myTmp"], mainWoobyDF_Adv["relativeValue_WU"])
plt.scatter(mainWoobyDF_Basic["myTmp"], mainWoobyDF_Basic["relativeValue_WU"])


fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(mainWoobyDF_Adv["thetadeg"], mainWoobyDF_Adv["relativeValue_WU"], mainWoobyDF_Adv["realWeight"], c=mainWoobyDF_Adv["realWeight"], marker='o')





fig = plt.figure()
ax = fig.gca(projection='3d')

# Make data.
X = np.arange(0, 40000, 100)
Y = np.arange(-30, 30, 0.5)
X, Y = np.meshgrid(X, Y)
Z = intercept_adv + coeffsreg_adv[0]*X + coeffsreg_adv[1]*abs(Y)

# Plot the surface.
surf = ax.plot_surface(X, Y, Z, cmap=cm.coolwarm,
                       linewidth=0, antialiased=False)

ax.view_init(0, -90)

# Customize the z axis.
ax.set_zlim(-1.01, 1.01)
ax.zaxis.set_major_locator(LinearLocator(10))
ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))

# Add a color bar which maps values to colors.
fig.colorbar(surf, shrink=0.5, aspect=5)

plt.show()







selected_feat = ["absThetadeg", "absPhideg"]
# selected_feat = ["relativeValue_WU" ,"absThetadeg"]
X_delta = np.array(mainWoobyDF_Adv[selected_feat])
y_delta = np.array(mainWoobyDF_Adv["relativeValue_WU"])


y_delta = y_delta.reshape((-1, 1))

reg_delta = LinearRegression().fit(X_delta, y_delta)

# The coefficients & interception
coeffsreg_delta = reg_delta.coef_[0]
intercept_delta = reg_delta.intercept_[0]

print('\n')
print('Coefficients (adv): \n',   coeffsreg_adv)
print('Intercept (adv): \n',      intercept_adv)
print('\n')


plt.figure()
plt.plot(y_delta, y_delta, 'o')






