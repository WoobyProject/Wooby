#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 14:40:59 2020

@author: enriquem
"""

R2 = 150e3#1.5e6
R1 = 100e3
 
# gamma_p = 0.358/4.2
gamma_p = 1.775/4.940

R_p= gamma_p/(1-gamma_p)*R2

R_esp = 1/(1/R_p - 1/R1 )

print("Calculated internal ESP impedance: {}".format(R_esp))
# R_esp = 1e6

# ----------------

V_in = 4.940
R_p = R_esp*R1/(R_esp+R1)

V_out = V_in*R_p/(R_p+R2)
V_out_ideal = V_in*R1/(R1+R2)

print("Real: {}".format(V_out))
print("Ideal: {}".format(V_out_ideal))