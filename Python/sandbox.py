#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 13 00:10:12 2020

@author: enriquem
"""

import numpy as np
import matplotlib.pyplot as plt

plt.figure()
vec_b = np.arange(-50,50, 10)
vec_b = [-50, -20, 0]

vec_offset = np.arange(-10,2, 2)

myX = np.arange(-30,31,1)


for offset in vec_offset:
#for b_test in vec:
    
    a_test = -2
    b_test = 0
    c_test = 1
    
    myY = c_test + b_test*(myX-offset) + a_test*((myX-offset)**2)
    

    plt.plot(myX, myY)
    
    
    
    
    
    
##################################     
#    Linear regression (coeffs theta)   #
################################## 

WoobyDataFrame["relativeValue"] = max(WoobyDataFrame["relativeVal_WU"])
WoobyDataFrame["relativeValue_WU_0"] = max(WoobyDataFrame["relativeVal_WU"])
        
WoobyDataFrame["thetasqr"] = WoobyDataFrame["thetadeg"]**2
selected_feat = ["thetasqr" ,"thetadeg"]

# selected_feat = ["relativeValue_WU" ,"absThetadeg"]
X_cf_th = np.array(WoobyDataFrame[selected_feat])
y_cf_th = np.array(WoobyDataFrame["relativeVal_WU"]/ WoobyDataFrame["relativeValue_WU_0"]-1)

X_cf_th = np.array(mainWoobyDF_Adv[selected_feat])
y_cf_th = np.array(mainWoobyDF_Adv["relativeValue_WU"]/ mainWoobyDF_Adv["relativeValue_WU_0"]-1)

X_cf_th = X_cf_th.reshape((-1, 2))
y_cf_th = y_cf_th.reshape((-1, 1))

reg_cf_th = LinearRegression().fit(X_cf_th, y_cf_th)

# The coefficients & interception
coeffsreg_cf_th = reg_cf_th.coef_
intercept_cf_th = reg_cf_th.intercept_

print('\n')
print('Coefficients: \n',   coeffsreg_cf_th)
print('Intercept: \n',      intercept_cf_th)
print('\n')

m_a_Xtreme = coeffsreg_cf_th[0][0]
m_b_Xtreme = coeffsreg_cf_th[0][1]

print('\n')
print('m_a_Xtreme: \n',   m_a_Xtreme)
print('m_b_Xtreme: \n',   m_b_Xtreme)
print('\n')

plt.figure()
plt.plot(y_cf_th, reg_cf_th.predict(X_cf_th), 'x')
plt.plot([-0.3, 0],[-0.3, 0])