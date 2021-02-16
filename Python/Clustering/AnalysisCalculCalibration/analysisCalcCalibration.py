#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 21:02:43 2021

@author: enriquem
"""

import numpy as np
import matplotlib.pyplot as plt

# %%

cf_0 = 42.57249674569516
b = 1542.57028666


W_wu = np.linspace(-62e3, 400e3, 10000)

W_gr = (1/cf_0)*W_wu + b


# %%

# Considering a mesure of W_wu0 giveng a perfect measure of W_gr0 
# and considering a nomial consolidation factor cf0

# Considering a change of the calibration factor of alpham such that 
# cf = alpha*cf0. 

# Considering a maximum error in gr of max_error = 5 gr and a maximum of the
# range max_range = 10e3 gr, the limits of alpha are
#  alpha > 1 / (1 - max_error/max_range)
#  alpha > 1 / (1 + max_error/max_range)

max_range = 10e3
max_error =  5

alpha_max = min(1 / (1 + max_error/max_range), 1 / (1 - max_error/max_range))
alpha_max = 1/(1 - max_error/(max_range - b))
alpha_min = 1/(1 + max_error/(max_range - b))


# %%

f1 = plt.figure()
f2 = plt.figure()

for alpha in np.linspace(0.9995, 1.0005, 7):
    W_gr_bias = (1/(cf_0*alpha)) * W_wu + b
    delta_W_gr = W_gr_bias - ((1/(cf_0))*W_wu + b)
    
    plt.figure(f1.number)
    plt.plot(W_wu,W_gr_bias,         label= "{:.4f}".format(alpha))
    
    plt.figure(f2.number)
    plt.plot(W_gr_bias,delta_W_gr,   label= "{:.4f}".format(alpha))
    
    
plt.figure(f1.number)
plt.grid()
plt.legend(loc="best")
plt.show()

plt.figure(f2.number)


W_gr_limit_max = (1/(cf_0*alpha_max)) * W_wu + b
delta_W_gr_limit_max = W_gr_limit_max - ((1/(cf_0))*W_wu + b)
plt.plot(W_gr, delta_W_gr_limit_max,   label= "Limit {:.4f}".format(alpha_max), color="black", linestyle="--", alpha=0.2)

W_gr_limit_min = (1/(cf_0*alpha_min)) * W_wu + b
delta_W_gr_limit_min = W_gr_limit_min - ((1/(cf_0))*W_wu + b)
plt.plot(W_gr, delta_W_gr_limit_min,   label= "Limit {:.4f}".format(alpha_min), color="black", linestyle="--", alpha=0.2)


plt.grid()
plt.legend(loc="best")
plt.show()
