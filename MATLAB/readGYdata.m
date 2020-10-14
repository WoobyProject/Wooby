function [ myGYdata ] = readGYdata(filedir,filename)


%%% Read values:
%   1) Time:    
%   2) Ax:      acceleration in x           	(bits) 
%   3) Ay:      acceleration in y            	(bits) 
%   4) Az:      acceleration in z               (bits)
%   5) T:       temperature                     (bits)  
%   6) Gx:           absolute time just before the measure           (ms) (and converted to s for this program)
%   7) Gy:            absolute time just after the measure            (ms) (and converted to s for this program)
%   8) Gz:       absolute time just after the measure            (gr) 

% 

% Heading
    myGYdata.filedir = filedir;
    myGYdata.filename = filename;
    myGYdata.LSBperg = 16384;   % or 32768/2
    myGYdata.LSBperdegs = 131;  % or 32768/250
    
% CSV read
    M = csvread(fullfile(filedir,filename));
    
% Reading 
    myGYdata.time =  M(:,1)/1000; % in s
    myGYdata.AxRaw = M(:,2); % in bits
    myGYdata.AyRaw = M(:,3); % in bits
    myGYdata.AzRaw = M(:,4); % in bits
    myGYdata.T  =    M(:,5); % in bits
    myGYdata.GxRaw = M(:,6); % in bits
    myGYdata.GyRaw = M(:,7); % in bits
    myGYdata.GzRaw = M(:,8); % in bits

% Calculating 
    myGYdata.Ax = myGYdata.AxRaw/myGYdata.LSBperg; % in g
    myGYdata.Ay = myGYdata.AyRaw/myGYdata.LSBperg; % in g
    myGYdata.Az = myGYdata.AzRaw/myGYdata.LSBperg; % in g
    
    myGYdata.Gx = myGYdata.GxRaw/myGYdata.LSBperdegs; % in deg/s
    myGYdata.Gy = myGYdata.GyRaw/myGYdata.LSBperdegs; % in deg/s
    myGYdata.Gz = myGYdata.GzRaw/myGYdata.LSBperdegs; % in deg/s

% myFrame adjustment
    myAx =   myGYdata.Ax;
    myAy =  -myGYdata.Az;
    myAz =   myGYdata.Ay;
    
    myGYdata.Ax = myAx; % in g
    myGYdata.Ay = myAy; % in g
    myGYdata.Az = myAz; % in g
end
