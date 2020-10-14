

nMeasures_vec = [1 2 3 4 5 7 10];
mean_vec = NaN*nMeasures_vec;
std_vec = NaN*nMeasures_vec;
meantimeMeasure_vec = NaN*nMeasures_vec;

filedir = '/Users/macretina/Documents/Humanity Lab/Wooby/MATLAB/datasets/study_nMeasures';


f1 = figure;

for i = 1:length(nMeasures_vec)
    
    nMeasures = nMeasures_vec(i);
    filename = sprintf('nMeasures_data_%dms_138gr.csv', nMeasures);
    
    % CSV loading
        M = csvread(fullfile(filedir,filename));
    
    % Nominal value
        iStr = regexp(filename, 'ms_'); iStr = iStr+3;
        iEnd = regexp(filename, 'gr');iEnd = iEnd(1)-1;
        nominalValue = str2num(filename(iStr:iEnd));

    % Reading 
        time_generic = M(:,1)/1000; % in s
        realValue_generic = M(:,2);
        correctedValue_generic = M(:,3);
        beforeMeasure_generic = M(:,4)/1000;
        afterMeasure_generic = M(:,5)/1000;
        realValueFiltered_generic = M(:,6);
        correctedValueFiltered_generic = M(:,7);

        OFFSET_generic = M(:,11);
        realValueWU_generic = M(:,12);


    % Calculation 
        timeMeasure_generic = afterMeasure_generic-beforeMeasure_generic;
        meantimeMeasure = mean(timeMeasure_generic);
        ndata_generic = length(time_generic);
        
        
        meanWU_generic = mean(realValueWU_generic);
        stdWU_generic = mean(realValueWU_generic);
        
        meanRawMesure_generic = mean(realValue_generic);
        stdRawMesure_generic  =  std(realValue_generic);
        
        meanDisplayMesure_generic = mean(correctedValueFiltered_generic);
        stdDisplayMesure_generic  =  std(correctedValueFiltered_generic);
        
    % Function creation
        meantimeMeasure_vec(i) = meantimeMeasure;
        
        meanRaw_vec(i) = meanRawMesure_generic;
        stdRaw_vec(i) = stdRawMesure_generic;
        
        mean_vec(i) = meanDisplayMesure_generic;
        std_vec(i) = stdDisplayMesure_generic;
        
        
     figure(f1)
        plot(time_generic-time_generic(1), correctedValueFiltered_generic, ...
            'DisplayName', sprintf('Samples/measure = %d', nMeasures))
        hold on
        
end

legend show 
grid on
xlabel('Normalized time (s)')
ylabel('Measurement (gr)')


%% n Analysis

measureRate_vec = 1000*meantimeMeasure_vec./nMeasures_vec; % in ms/measurement

figure
    plot(nMeasures_vec,measureRate_vec, '+--' )
    grid on
    xlabel('Number of data by measurement (nMeasures) ')
    ylabel('Time/measurement (ms/mes)')
    title('Time per measurement (ms/mes)')

figure
    plot(nMeasures_vec,stdRaw_vec, '*--', 'DisplayName', 'Raw data' )
    hold on
    plot(nMeasures_vec,std_vec, '+--', 'DisplayName', 'Displayed data' )
    grid on
    xlabel('Number of data by measurement (nMeasures) ')
    ylabel('Time/measurement (ms/mes)')
    title('Standard deviation (gr)')
    legend show
    