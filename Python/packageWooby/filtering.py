import scipy
from scipy import signal
from scipy.fft import fft
import matplotlib.pyplot as plt

# Check http://web.cecs.pdx.edu/~tymerski/ece452/6.pdf 

def genericFilter(time, inputSignal, num, den, Te):
    
    tfFilter = signal.TransferFunction(num, den, dt=Te)
    resultFilter = signal.dlsim(tfFilter, inputSignal, time)
    
    return resultFilter
    
def filter_1od(time, inputSignal, tau, Te):

    a = 1 - math.exp(-Te/tau)
    b = math.exp(-Te/tau)
    
    num = [a]
    den = [1, -b]

    tfFilter = signal.TransferFunction(num, den, dt=Te)
    resultFilter = signal.dlsim(tfFilter, inputSignal, time, inputSignal[0])
    
    return resultFilter



def movingAvg(inputSignal, n):
    if not isinstance(inputSignal, pd.DataFrame):
        inputSignalSeries = pd.Series(inputSignal)
        
    resultFilter = inputSignalSeries.rolling(window=n).mean()
    
    return np.array(resultFilter)


def myFFT(time, inputSignal, plot=False, fig=None):
    
    time = WoobyDataFrame["timeNorm"]/1000
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







    