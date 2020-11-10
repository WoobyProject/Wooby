#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 23:17:57 2020

@author: enriquem
"""

##################################        
#       Loading file             #
##################################

fileFolder = "/Users/macretina/Documents/Airbus/Humanity Lab/Wooby/Github/Python/datasets/Austin"
fileName = "Austin_104gr_Measure1.txt"
fileName = "Austin_104gr_Up_Box_Empty.txt"

WoobyData = readWoobyFile(fileFolder, fileName, verbose=True)
WoobyDataFrame = WoobyData["data"]


##################################        
#      Filtering                 #
##################################

index = (WoobyDataFrame["timeNorm"]>270000) & (WoobyDataFrame["timeNorm"]<315000)
# index = (WoobyDataFrame["timeNorm"]>20000) & (WoobyDataFrame["timeNorm"]<60000)
WoobyDataFrameNoFilt = WoobyDataFrame 
WoobyDataFrame = WoobyDataFrame.loc[index]


##################################        
#      Calculations              #
##################################

iCol = WoobyDataFrame.columns.get_loc('realValueFiltered')
WoobyDataFrame['SMA_7'] = WoobyDataFrame.iloc[:,iCol].rolling(window=7).mean()

iCol = WoobyDataFrame.columns.get_loc('realValueFiltered')
WoobyDataFrame['SMA_15'] = WoobyDataFrame.iloc[:,iCol].rolling(window=15).mean()


iCol = WoobyDataFrame.columns.get_loc('realValueFiltered')
WoobyDataFrame['SMM_7'] = WoobyDataFrame.iloc[:,iCol].rolling(window=7).median()


iCol = WoobyDataFrame.columns.get_loc('realValueFiltered')
WoobyDataFrame['SMM_15'] = WoobyDataFrame.iloc[:,iCol].rolling(window=15).median()



iCol = WoobyDataFrame.columns.get_loc('realValue_WU')
WoobyDataFrame['realValue_WU_SMA_10'] = WoobyDataFrame.iloc[:,iCol].rolling(window=10).mean()

iCol = WoobyDataFrame.columns.get_loc('realValue_WU')
WoobyDataFrame['realValue_WU_SMA_15'] = WoobyDataFrame.iloc[:,iCol].rolling(window=15).mean()

iCol = WoobyDataFrame.columns.get_loc('realValue_WU')
WoobyDataFrame['realValue_WU_SMA_5'] = WoobyDataFrame.iloc[:,iCol].rolling(window=5).mean()



condition = (WoobyDataFrame["timeNorm"]>262000) & (WoobyDataFrame["timeNorm"]<320000)
WoobyDataFrame['artificialRealWeight'] = 4480*condition


minOverall = min( WoobyDataFrame["correctedValueFiltered"])
maxOverall = max( WoobyDataFrame["correctedValueFiltered"])
avgOverall = np.mean( WoobyDataFrame["correctedValueFiltered"])
stdOverall = np.std( WoobyDataFrame["correctedValueFiltered"])




##################################        
#      Plots                     #
##################################

plt.figure()
plt.plot(WoobyDataFrame["timeNorm"], WoobyDataFrame["realValue_WU"]/WoobyDataFrame["calibrationFactor"], marker='+',            label="realValue_WU")
plt.plot(WoobyDataFrame["timeNorm"], WoobyDataFrame["realValue_WU_SMA_10"]/WoobyDataFrame["calibrationFactor"], marker='+',     label="realValue_WU_SMA_10")
plt.plot(WoobyDataFrame["timeNorm"], WoobyDataFrame["realValue_WU_SMA_15"]/WoobyDataFrame["calibrationFactor"], marker='+',     label="realValue_WU_SMA_15")
plt.plot(WoobyDataFrame["timeNorm"], WoobyDataFrame["realValue_WU_SMA_5"]/WoobyDataFrame["calibrationFactor"], marker='*',      label="realValue_WU_SMA_5")
plt.show()
plt.grid(True)
plt.legend(loc="best")



plt.figure()
plt.plot(WoobyDataFrame["timeNorm"][1:], WoobyDataFrame["timeNorm"][1:], '+--')
plt.plot(WoobyDataFrame["timeNorm"][1:], WoobyDataFrame["timeNorm"][0:-1].to_numpy() , '*--')
         
         
plt.figure()
plt.plot(WoobyDataFrame["timeNorm"], WoobyDataFrame["thetadeg"], label ="thetadeg")
plt.plot(WoobyDataFrame["timeNorm"], WoobyDataFrame["phideg"], label ="phideg")
plt.show()
plt.grid(True)




plt.plot([1, 2, 3, 4])


plt.subplot(221)
plt.plot(WoobyDataFrame["timeNorm"]/1000, WoobyDataFrame["myAx"], label="Ax")
plt.plot(WoobyDataFrame["timeNorm"]/1000, WoobyDataFrame["myAy"], label="Ay")
plt.plot(WoobyDataFrame["timeNorm"]/1000, WoobyDataFrame["myAz"], label="Az")
plt.legend(loc='best')
plt.grid(True)
plt.show()


plt.subplot(222)
plt.plot(WoobyDataFrame["timeNorm"]/1000, WoobyDataFrame["myGx"], label="Gx")
plt.plot(WoobyDataFrame["timeNorm"]/1000, WoobyDataFrame["myGy"], label="Gy")
plt.plot(WoobyDataFrame["timeNorm"]/1000, WoobyDataFrame["myGz"], label="Gz")
plt.legend(loc='best')
plt.grid(True)
plt.show()

plt.subplot(223)
plt.plot(WoobyDataFrame["timeNorm"]/1000, WoobyDataFrame["thetadeg"], label ="thetadeg")
plt.plot(WoobyDataFrame["timeNorm"]/1000, WoobyDataFrame["phideg"], label ="phideg")
plt.show()
plt.grid(True)
plt.legend(loc='best')


plt.subplot(224)
plt.figure()
plt.plot(WoobyDataFrame["timeNorm"]/1000, WoobyDataFrame["relativeVal_WU"]/42.7461, label="rawValue")
plt.plot(WoobyDataFrame["timeNorm"]/1000, WoobyDataFrame["realValue"],  ls="--", label="realValue")
plt.plot(WoobyDataFrame["timeNorm"]/1000, (WoobyDataFrame["relativeVal_WU"]/(1+( -0.00014)*WoobyDataFrame["thetadeg"]**2))/42.7461,  ls="--", label="realValue")
plt.plot(WoobyDataFrame["timeNorm"]/1000, WoobyDataFrame["SMA_7"],  ls="--", label="Moving avg (7)")
plt.plot(WoobyDataFrame["timeNorm"]/1000, WoobyDataFrame["SMA_15"],  ls="--", label="Moving avg (15)")

plt.plot(WoobyDataFrame["timeNorm"]/1000, WoobyDataFrame["SMM_7"],  ls="--", label="Moving median (7)")
plt.plot(WoobyDataFrame["timeNorm"]/1000, WoobyDataFrame["SMM_15"],  ls="--", label="Moving median (15)")

      
'''
plt.plot(WoobyDataFrame["timeNorm"]/1000, WoobyDataFrame["realValueFiltered"], label="realValueFiltered")
plt.plot(WoobyDataFrame["timeNorm"]/1000, WoobyDataFrame["correctedValueFiltered"], label="correctedValueFiltered")
'''




plt.plot(WoobyDataFrame["timeNorm"]/1000, WoobyDataFrame["artificialRealWeight"], 'k--')
plt.plot(WoobyDataFrame["timeNorm"]/1000, WoobyDataFrame["artificialRealWeight"]-5, 'k--')
plt.plot(WoobyDataFrame["timeNorm"]/1000, WoobyDataFrame["artificialRealWeight"]+5, 'k--')
'''
plt.plot(WoobyDataFrame["timeNorm"]/1000, [avgOverall  ]* WoobyDataFrame.shape[0], 'k--')
plt.plot(WoobyDataFrame["timeNorm"]/1000, [avgOverall-5]* WoobyDataFrame.shape[0], 'k--')
plt.plot(WoobyDataFrame["timeNorm"]/1000, [avgOverall+5]* WoobyDataFrame.shape[0], 'k--')
'''
plt.show()
plt.grid(True)
plt.legend(loc="best")



### Error calculation

error_SMA_7  = np.sum((WoobyDataFrame["realWeight"] - WoobyDataFrame["SMA_7"])*2)
error_SMA_15 = np.sum((WoobyDataFrame["realWeight"] - WoobyDataFrame["SMA_15"])*2)
error_SMM_7  = np.sum((WoobyDataFrame["realWeight"] - WoobyDataFrame["SMM_7"])*2)
error_SMM_15 = np.sum((WoobyDataFrame["realWeight"] - WoobyDataFrame["SMM_15"])*2)


'''
error_SMA_7  = np.sum((WoobyDataFrame["artificialRealWeight"] - WoobyDataFrame["SMA_7"])*2)
error_SMA_15 = np.sum((WoobyDataFrame["artificialRealWeight"] - WoobyDataFrame["SMA_15"])*2)
error_SMM_7  = np.sum((WoobyDataFrame["artificialRealWeight"] - WoobyDataFrame["SMM_7"])*2)
error_SMM_15 = np.sum((WoobyDataFrame["artificialRealWeight"] - WoobyDataFrame["SMM_15"])*2)
'''

print("Error for SMA_7: {}".format(error_SMA_7))
print("Error for SMA_15: {}".format(error_SMA_15))
print("Error for SMM_7: {}".format(error_SMM_7))
print("Error for SMM_15: {}".format(error_SMM_15))


### Frequency comparison calculation
FFT_relativeVal  = myFFT(WoobyDataFrame["timeNorm"]/1000,     WoobyDataFrame["realValue"])
FFT_realValueFilt = myFFT(WoobyDataFrame["timeNorm"]/1000,     WoobyDataFrame["realValueFiltered"])
FFT_SMA_7  = myFFT(WoobyDataFrame["timeNorm"][7:]/1000, WoobyDataFrame["SMA_7"][7:])
FFT_SMA_15 = myFFT(WoobyDataFrame["timeNorm"][15:]/1000,WoobyDataFrame["SMA_15"][15:])
FFT_SMM_7  = myFFT(WoobyDataFrame["timeNorm"][7:]/1000, WoobyDataFrame["SMM_7"][7:])
FFT_SMM_15 = myFFT(WoobyDataFrame["timeNorm"][15:]/1000,WoobyDataFrame["SMM_15"][15:])


   
figFFT = plt.figure()   
plt.plot(FFT_relativeVal[0],    FFT_relativeVal[1],     label="relativeVal")
plt.plot(FFT_realValueFilt[0],  FFT_realValueFilt[1],   label="realValueFiltered")
plt.plot(FFT_SMA_7[0],          FFT_SMA_7[1],           label="FFT_SMA_7")
plt.plot(FFT_SMA_15[0],         FFT_SMA_15[1],          label="FFT_SMA_15")
plt.plot(FFT_SMM_7[0],          FFT_SMM_7[1],           label="FFT_SMM_7")
plt.plot(FFT_SMM_15[0],         FFT_SMM_15[1],          label="FFT_SMM_15")
plt.grid(True)
plt.legend(loc="best")

'''
plt.figure()
plt.plot(WoobyDataFrame["timeNorm"]/1000, (1/42.7461)*(WoobyDataFrame["realValue_WU"]-WoobyDataFrame["OFFSET"]), label="rawValue")
plt.plot(WoobyDataFrame["timeNorm"]/1000, (1/42.7461)*WoobyDataFrame["relativeVal_WU"], ls="--", label="rawValue")
plt.plot(WoobyDataFrame["timeNorm"]/1000, (1/42.7461)*WoobyDataFrame["relativeVal_WU"]/(1+( -0.00014)*WoobyDataFrame["thetadeg"]**2), ls="--", label="rawValue")

'''



plt.figure()
condensed = WoobyDataFrame["realValue"].append(WoobyDataFrame["realValueFiltered"]).append(WoobyDataFrame["correctedValueFiltered"])
minVal = math.floor(min(condensed)) 
maxVal = math.ceil(max(condensed))
bins = np.linspace(minVal, maxVal, round(math.sqrt(WoobyDataFrame.shape[0])))
plt.hist(WoobyDataFrame["realValue"],               bins=bins, alpha=0.5, ec='black', label="realValue")
plt.hist(WoobyDataFrame["realValueFiltered"],       bins=bins, alpha=0.5, ec='black', label="realValueFiltered")
plt.hist(WoobyDataFrame["correctedValueFiltered"],  bins=bins, alpha=0.5, ec='black', label="correctedValueFiltered")
plt.legend(loc='best')
plt.grid(True)
plt.show()