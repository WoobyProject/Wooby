%% %% Temp study %%%%


    filedir = fullfile(fileparts(matlab.desktop.editor.getActiveFilename), 'datasets/study_Temp');
    
    filename = 'Temp_data_7ms_0gr_BAT.csv';
    filename = 'Temp_data_7ms_10gr_BAT.csv';
    filename = 'Temp_data_7ms_500gr_BAT.csv';
    filename = 'Temp_data_7ms_500gr_BAT_Mismatch.csv';
    
    filename = 'Temp_data_7ms_500gr_BAT_CorrectionTemp.csv';
    
    filename = 'Temp_data_7ms_500gr_BAT_hanging.csv';
    
%     filename = 'Temp_data_7ms_500gr_BAT_hanging_cooling2.csv';

    filename = 'Temp_data_7ms_500gr_BAT_hanging_allTemps.csv';
    
    filename = 'Temp_data_7ms_500gr_BAT_correctedLinear.csv';
    

    dataTemp = readWoobyData(filedir,filename, Inf);
    
%     filedir = '/Users/macretina/Documents/Humanity Lab/Wooby/MATLAB/datasets/study_Temp';
%     filename = 'Temp_data_7ms_0gr_NOBAT.csv';
%     data0grNOBAT = readWoobyData(filedir,filename);

index = dataTemp.time>240;

%% Plots

figure
    plot( dataTemp.time(index), dataTemp.Temp(index), '--', 'Color', [ 0.5, 0.5, 0.5])
    hold on 
    scatter( dataTemp.time(index), dataTemp.Temp(index), [], dataTemp.Temp(index),  'DisplayName',   dataTemp.filename)
    grid on
    legend show
    ylabel('Temperature(C)')
    xlabel('Time (s)')
    title('Temperature behaviour')
    
figure
    plot( dataTemp.time(index), dataTemp.realValue(index), '--', 'Color', [ 0.5, 0.5, 0.5])
    hold on 
%     scatter( dataTemp.time(index), dataTemp.realValue(index), [], dataTemp.Temp(index),  'DisplayName',   dataTemp.filename)
    grid on
    legend show
    ylabel('Real weight measurement(gr)')
    xlabel('Time (s)')
    title('Real weight behaviour')
    
figure
    plotyy(dataTemp.time(index), dataTemp.Temp(index)-dataTemp.TempRef(index),dataTemp.time(index), -(dataTemp.realValueWU(index)-dataTemp.OFFSET(index))) 
    grid on
    
figure
    ax = plotyy(dataTemp.time(index), dataTemp.Temp(index)-dataTemp.TempRef(index),dataTemp.time(index), dataTemp.realValue(index)-dataTemp.nominalValueVec(index)) 
    grid on
    hold on
figure
    ax = plotyy(dataTemp.time(index), dataTemp.Temp(index)-dataTemp.TempRef(index),dataTemp.time(index), dataTemp.TempCorrectionValue(index)) 
    grid on
    hold on
    
figure
    plot(dataTemp.time(index), dataTemp.realValue(index))
    hold on
    plot(dataTemp.time(index), dataTemp.realValue(index)-dataTemp.TempCorrectionValue(index))
    plot(dataTemp.time(index), dataTemp.realValue(index)- (-46.1224*0.9*(dataTemp.Temp(index)-dataTemp.TempRef(index))/(-61.7977)))
    grid on
    
    figure
    plot(dataTemp.time(index), dataTemp.TempCorrectionValue(index))
    hold on
    plot(dataTemp.time(index), -46.1224*(dataTemp.Temp(index)-dataTemp.TempRef(index))/(-61.7977))
    
% figure
%     plot( dataTemp.time, dataTemp.correctedValue, '--', 'Color', [ 0.5, 0.5, 0.5])
%     hold on 
%     scatter( dataTemp.time, dataTemp.correctedValue, [], dataTemp.Temp,  'DisplayName',   dataTemp.filename)
%     grid on
%     legend show
%     ylabel('Corrected weight measurement(gr)')
%     xlabel('Time (s)')
%     title('Corrected weigth behaviour')
%     
% figure
%     plot( dataTemp.time(index), dataTemp.realValueWU(index), '--', 'Color', [ 0.5, 0.5, 0.5])
%     hold on 
%     scatter( dataTemp.time(index), dataTemp.realValueWU(index), [], dataTemp.Temp(index),  'DisplayName',   dataTemp.filename)
%     grid on
%     legend show
%     ylabel('Real weight measurement(gr)')
%     xlabel('Time (s)')
%     title('NO UNITS weight behaviour')

figure
    plot( dataTemp.Temp(index), dataTemp.realValue(index), '--', 'Color', [ 0.5, 0.5, 0.5])
    hold on 
    scatter(dataTemp.Temp(index), dataTemp.realValue(index), [], dataTemp.time(index),  'DisplayName',   dataTemp.filename)
    
%     deltaTemp = dataTemp.Temp-dataTemp.Temp(1);
%     tempCorrectionFactor = polyval(Pfinal,deltaTemp);   
%     
%     scatter(dataTemp.Temp, dataTemp.realValue./tempCorrectionFactor, [], 'k',  'Marker', '+', 'DisplayName',   dataTemp.filename)
    
    grid on
    legend show
    ylabel('Real weight measurement(gr)')
    xlabel('Temperature (C)')
    title('Real weigth behaviour')
    colorbar

   
figure
%     plot( dataTemp.Temp(index), dataTemp.realValueWU(index), '--', 'Color', [ 0.5, 0.5, 0.5])
    hold on 
    scatter(dataTemp.Temp(index), dataTemp.realValueWU(index), [], dataTemp.time(index),  'DisplayName',   dataTemp.filename)
    grid on
    legend show
    ylabel('Real weight measurement(WU)')
    xlabel('Temperature (C)')
    title('Real weigth behaviour')
    colorbar
    
    % ./dataTemp.OFFSET(index)
    % -dataTemp.TempRef(index)
    
    
    
figure
%     plot( dataTemp.Temp(index), dataTemp.realValueWU(index), '--', 'Color', [ 0.5, 0.5, 0.5])
    hold on 
    scatter( dataTemp.nominalValueVec(index), dataTemp.realValueWU(index),  [], dataTemp.Temp(index),  'DisplayName',   dataTemp.filename)
    grid on
    legend show
    ylabel('Real weight measurement(WU)')
    xlabel('Weight value (gr)')
    title('Real weigth behaviour')
    c = colorbar; c.Label.String = 'Temperature (C)';
    
        
%%

TEMPREF = 35;         % central Temperature  
WUREF = 2.65e4; 
%2.4867e+04;  % from model calcualted in study_wu_vs_gr accordgin to Wooby v1 @ 500 gr

index = dataTemp.time>200;

dataX = dataTemp.Temp-TEMPREF;
dataY = dataTemp.realValueWU;

dataSelectedX = dataTemp.Temp(index)-TEMPREF;
dataSelectedY = dataTemp.realValueWU(index)+WUREF;

% Data selection for fitting
    t = dataSelectedX;
    y = dataSelectedY;

% With polyfit
    P = polyfit(t, y, 3);
    % P(4) = P(4)-0.0095;
    % P = [  -7.9473e-07,  9.3144e-06,  0.0018,   0.9996];


% With lsqsin
    A = [];     % No inequality constraint
    b = [];     % No inequality constraint
    d = y;
    
    % For first order
    C = [t ones(size(t))];

    
    % For thrid order
%     C = [t.^3 t.^2 t ones(size(t))];
%     Aeq = [0    0    0    1];   % t = 0
    
    % If forced to be in a specific point
%         Aeq = [0   1];   % t = 0
%         beq = [1];                  % y = 1 (when t = 0)

    % If forced to be in a specific point
        Aeq = [0   1];   % t = 0
        beq = [0];                  % y = 1 (when t = 0)

    % If NOT forced to be in a specific point
%         Aeq = [];   
%         beq = [];
         
    x_lsqlin1 = lsqlin(C,d,A,b,Aeq,beq);
    P = x_lsqlin1;
    
%     Pfinal = [  -1.2349e-06, 1.3114e-05, 0.0019, 1];
    
    
% Coeffs
    for ii=1:length(P)
        fprintf('\nP_%d = %f;\n', length(P)-ii, P(ii))
    end
    
% Fitted data
    fittedData = polyval(P,dataX);   

% tempRef = polyval(P,26);   
% vq = interp1(fittedData,sort(dataTemp.Temp),1)

%%
figure
%     scatter(  dataSelectedX,   dataSelectedY, [], [1, 0, 0], 'DisplayName',   dataTemp.filename)
    hold on
%     scatter(  dataTemp.Temp(:), dataTemp.realValue(:)/dataTemp.nominalValue,  [] ,[0, 1, 0])
    scatter(  t,   y, [], t, 'DisplayName',   dataTemp.filename, 'Marker', '+')
     plot(dataX, fittedData)
    hold on
    grid on
    legend show
    xlabel(sprintf('\\Delta Temperature(C) (T_{ref} = %.2f C)', TEMPREF))
    ylabel('Real weight (gr)')
    title('Offset behaviour')
    colorbar
    