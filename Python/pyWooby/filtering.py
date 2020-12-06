
from scipy import signal
from scipy.fft import fft
import matplotlib.pyplot as plt
import math
import numpy as np
import pandas as pd

# Documentation: http://web.cecs.pdx.edu/~tymerski/ece452/6.pdf 

def genericFilter(time, inputSignal, num, den, Te):
    
    tfFilter = signal.TransferFunction(num, den, dt=Te)
    resultFilter = signal.dlsim(tfFilter, inputSignal, time)
    
    return resultFilter
    
def filter_1od(time, inputSignal, tau, Te):

    time = np.array(time)
    inputSignal = np.array(inputSignal)
        
    b = 1 - math.exp(-Te/tau)
    a = math.exp(-Te/tau)
    
    num = [b]
    den = [1, -a]
    # filter =  y/u = b/(z-a)

    tfFilter = signal.TransferFunction(num, den, dt=Te)
    resultFilter = signal.dlsim(tfFilter, inputSignal, time, inputSignal[0])
    
    return resultFilter # returns a tuple with the values of tout and yout



def movingAvg(inputSignal, n):
    if not isinstance(inputSignal, pd.DataFrame):
        inputSignalSeries = pd.Series(inputSignal)
        
    resultFilter = inputSignalSeries.rolling(window=n).mean()
    
    return np.array(resultFilter)


def myFFT(time, inputSignal, plot=False, fig=None):
    
    y = np.array(inputSignal)
    
    # Number of sample points
    N = inputSignal.shape[0]
    # sample spacing
    T = time[1]-time[0]
    # FFT calculation
    yf = fft(y)
    ynorm = 2.0/N * np.abs(yf[0:N//2])
    freq = np.linspace(0.0, 1.0/(2.0*T), N//2)
    
    if (plot):
        if(fig!=None):
           plt.figure(fig.num)
        else:
            plt.figure()
        plt.plot(freq, ynorm)
        plt.grid()
        plt.xlabel("Frequency (Hz)")
        plt.ylabel("Magnitude")
        plt.show()

    return (freq, ynorm)


def mapval( x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;


    