function [ P1, f ] = myfft( t, X )
%UNTITLED2 Summary of this function goes here
%   Detailed explanation goes here

                
T = t(2)-t(1);          % Sampling period     
Fs = 1/T;               % Sampling frequency    
L = length(X);          % Length of signal

Y = fft(X);

P2 = abs(Y/L);
P1 = P2(1:L/2+1);
P1(2:end-1) = 2*P1(2:end-1);

f = Fs*(0:(L/2))/L;
loglog(f,P1) ; %semilogy
title('Single-Sided Amplitude Spectrum of X(t)')
xlabel('f (Hz)')
ylabel('|P1(f)|')
hold on 
grid on

end

