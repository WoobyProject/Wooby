function [ myWoobyData ] = readWoobyData(filedir,filename, tCutOff)

%%% Read values:
%   1) time:                    time after the code has started                 (ms) (and converted to s for this program)
%   2) realValue:               real value measured by the sensor               (gr) 
%   3) correctedValue:          value corrected with the first round algo       (gr)
%   4) beforeMeasure:           absolute time just before the measure           (ms) (and converted to s for this program)
%   5) afterMeasure:            absolute time just after the measure            (ms) (and converted to s for this program)
%   6) realValueFiltered:       absolute time just after the measure            (gr) 
%   7) correctedValueFiltered:  absolute time just after the measure            (gr)
%   8) bSync:                   boolean to indicate a sync (real value)         (wu)
%   9) bSyncCorrected:          boolean to indicate a sync (corrected value)    (wu)
%  10) calibration_factor:
%  11) scaleoffset
%  12) realValueWU:             value output wu of the weight sensor            (wu)


%  13) bInactive:               output Voltage of the Airduino                  (wu)
%  14) lastTimeActivity:        output Voltage of the Airduino                  (ms)
%  15) Vcc:                     output Voltage of the Airduino                  (V)
%  
%  16) Ax:                      acceleration in x body axe                      (g)
%  17) Ay:                      acceleration in y body axe                      (g)
%  18) Az:                      acceleration in z body axe                      (g)
%  19) Gyrox:                   speed of phi (x)                                (deg/s)
%  20) Gyroy:                   speed of theta (y)                              (deg/s)
%  21) Gyroz:                   speed of psi (z)                                (deg/s)

%  22) theta:                   Calculated theta angle                          (deg)
%  23) phi:                     Calculated phi angle                            (deg)
%  24) Temp:                    Temperature of the gyro                         (C)
%  25) Temp Ref:                Temperautre ref taken at the last TARE          (C)

if nargin < 3
   tCutOff = Inf; 
end

% Heading
    myWoobyData.filedir = filedir;
    myWoobyData.filename = filename;
    
% CSV read
    M = csvread(fullfile(filedir,filename));
    M = M( (M(:,1)/1000)<tCutOff , :);
    
    if isempty(M)
        error('The cutoff time is not valid')
    end
        
% Nominal value
    iStr = regexp(filename, 'ms_'); iStr = iStr+3;
    iEnd = regexp(filename, 'gr');iEnd = iEnd(1)-1;
    myWoobyData.nominalValue = str2double(filename(iStr:iEnd));

% Reading 
    myWoobyData.time =                      M(:,1)/1000; % in s
    myWoobyData.realValue =                 M(:,2);
    myWoobyData.correctedValue =            M(:,3);
    myWoobyData.beforeMeasure =             M(:,4)/1000;
    myWoobyData.afterMeasure =              M(:,5)/1000;
    myWoobyData.realValueFiltered =         M(:,6);
    myWoobyData.correctedValueFiltered =	M(:,7);
    
    myWoobyData.OFFSET =                    M(:,11);
    myWoobyData.realValueWU =               M(:,12);
        
    myWoobyData.Vcc =                       M(:,15);
    
    myWoobyData.Ax =                        M(:,16);
    myWoobyData.Ay =                        M(:,17);   
    myWoobyData.Az =                        M(:,18);                   
    myWoobyData.Gyrox =                     M(:,19);  
    myWoobyData.Gyroy =                     M(:,20);  
    myWoobyData.Gyroz =                     M(:,21);  

    myWoobyData.theta =                     M(:,22);  
    myWoobyData.phi =                       M(:,23);  
    myWoobyData.Temp =                      M(:,24);
    myWoobyData.TempRef =                   M(:,25);
    
    myWoobyData.TempCorrectionValue =     	M(:,26);
    
% Calculation 
    myWoobyData.ndata = length(myWoobyData.time);
    myWoobyData.timeNorm = myWoobyData.time-myWoobyData.time(1); 
    myWoobyData.diffMeasure = myWoobyData.afterMeasure-myWoobyData.beforeMeasure;
    myWoobyData.meandiffMeasure = mean(myWoobyData.diffMeasure);
    myWoobyData.calculation_time = myWoobyData.afterMeasure-myWoobyData.time;
    myWoobyData.timeMeasure = (myWoobyData.time(end)-myWoobyData.time(1));
    myWoobyData.meanrealValueWU = mean(myWoobyData.realValueWU);
    myWoobyData.erroRealValue = myWoobyData.realValue -  myWoobyData.nominalValue;
    
    myWoobyData.meanVcc = mean(myWoobyData.Vcc);
    
    myWoobyData.nominalValueVec = myWoobyData.nominalValue*ones(size(myWoobyData.time));
    myWoobyData.timeNorm = myWoobyData.time - myWoobyData.time(1);  
    
    myWoobyData.timeCorrected = linspace(myWoobyData.time(1), myWoobyData.time(end), length(myWoobyData.time));
    myWoobyData.timeCorrectedNorm = myWoobyData.timeCorrected - myWoobyData.timeCorrected(1);
    
% To be replaced by the real Arduino filtering    
    tau_f_angle = 2;
    filter = tf(1, [tau_f_angle 1]);
    
    myWoobyData.thetaFiltered = lsim(filter, myWoobyData.theta, myWoobyData.timeCorrectedNorm, myWoobyData.theta(1));
    myWoobyData.phiFiltered = lsim(filter, myWoobyData.phi, myWoobyData.timeCorrectedNorm, myWoobyData.phi(1));

end

