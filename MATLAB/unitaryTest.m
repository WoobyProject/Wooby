%% Generic Unitary Test

% filedir = '/Users/macretina/Documents/Humanity Lab/Wooby/MATLAB/datasets/Ursa_Major';


%%%% U Major %%%%

    % filename = 'UMajor_data_10ms_0gr_1.csv';
    % filename = 'UMajor_data_10ms_1009gr_1.csv';	
    % filename = 'UMajor_data_10ms_1513gr_1.csv';	
    % filename = 'UMajor_data_10ms_504gr_1.csv';
    % filename = 'UMajor_data_10ms_0gr_2.csv';
    % filename = 'BAD_UMajor_data_10ms_1009gr_2.csv';	
    % filename = 'UMajor_data_10ms_2513gr_1.csv';

    % filename = 'UMajor_data_10ms_0gr_101.csv';
    % filename = 'UMajor_data_10ms_1009gr_101.csv';
    % filename = 'UMajor_data_10ms_2009gr_101.csv';

    % filename = 'UMajor_data_10ms_0gr_201.csv';
    % filename = 'UMajor_data_10ms_1009gr_201.csv';
    % filename = 'UMajor_data_10ms_2009gr_202.csv';
    % filename = 'UMajor_data_10ms_0gr_202.csv';


%%%% Wooby v1 %%%%

    filedir = '/Users/macretina/Documents/Humanity Lab/Wooby/MATLAB/datasets/Wooby_v1';

    % filename = 'CALIB_Wooby_v1_data_10ms_0gr_1.csv';
    % filename = 'CALIB_Wooby_v1_data_10ms_503gr_1.csv';
    % filename = 'CALIB_Wooby_v1_data_10ms_1009gr_1.csv';
    % filename = 'CALIB_Wooby_v1_data_10ms_1513gr_1.csv';

    % filename = 'Wooby_v1_data_10ms_1000gr_1.csv';
    % filename = 'Wooby_v1_data_10ms_1000gr_moving.csv';

    filename = 'Wooby_v1_data_10ms_1009gr_moving.csv';
    filename = 'Wooby_v1_data_10ms_1009gr_below_moving_lat.csv';

    filename = 'Wooby_v1_data_7ms_138gr_below_moving_lat.csv';
    filename = 'Wooby_v1_data_10ms_5200gr_below_moving_long.csv';
    
    filename = 'Wooby_v1_data_7ms_1422gr_hanging_test.csv';

%%%% Wooby v2 %%%%

    % filedir = '/Users/macretina/Documents/Humanity Lab/Wooby/MATLAB/datasets/Wooby_v2';
    % filename = 'Wooby_v2_data_10ms_1513gr_1.csv';

%%%% nMeasurements study %%%%

    % filedir = '/Users/macretina/Documents/Humanity Lab/Wooby/MATLAB/datasets/study_nMeasures';
    % 
    % filename = 'nMeasures_data_1ms_138gr.csv';	
    % filename = 'nMeasures_data_2ms_138gr.csv';
    % filename = 'nMeasures_data_5ms_138gr.csv';
    % filename = 'nMeasures_data_10ms_138gr.csv';
    % filename = 'nMeasures_data_20ms_138gr.csv';	

%%%% Vcc study %%%%

%     filedir = '/Users/macretina/Documents/Humanity Lab/Wooby/MATLAB/datasets/study_Vcc';
%     filename = 'Vcc_data_7ms_0gr.csv';
%     filename = 'Vcc_data_7ms_0gr_Vccchanged.csv';
    


M = csvread(fullfile(filedir,filename));

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
%  12) realValueWU_generic:     value output wu of the weight sensor            (wu)


%  13) bInactive:               output Voltage of the Airduino                  (wu)
%  14) lastTimeActivity:        output Voltage of the Airduino                  (ms)
%  15) Vcc:                     output Voltage of the Airduino                  (V)
%  
%
                
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
        
    Vcc_generic = M(:,15);
    
% Calculation 
    diffMeasure_generic = afterMeasure_generic-beforeMeasure_generic;
    meandiffMeasure_generic = mean(diffMeasure_generic);
    ndata_generic = length(time_generic);
    calculation_time_generic = afterMeasure_generic-time_generic;
    timeMeasure = (time_generic(end)-time_generic(1));
    mean(realValueWU_generic);
  
%% Plots

x_min = min( [ realValue_generic ]);
x_max = max( [ realValue_generic ]);
x_min = floor(x_min);
x_max = ceil(x_max);


figure
    plot(time_generic, nominalValue*ones(size(time_generic)), '--', 'LineWidth', 3)
    hold on
    plot(time_generic, realValue_generic)
    plot(time_generic, correctedValue_generic)
    plot(time_generic, realValueFiltered_generic)
    plot(time_generic, correctedValueFiltered_generic)
    grid on
    legend('Nomimal', 'Real', 'Corrected', 'Real filtered (arduino)','Corrected filtered (arduino)' )

    nBins = 50;
figure
    histogram(realValue_generic, linspace(x_min, x_max, nBins),'Normalization','pdf')
    hold on
    histogram(correctedValue_generic, linspace(x_min, x_max, nBins),'Normalization','pdf')
    histogram(realValueFiltered_generic, linspace(x_min, x_max, nBins),'Normalization','pdf')
    histogram(correctedValueFiltered_generic, linspace(x_min, x_max, nBins),'Normalization','pdf') % 
    grid on
    legend('Real', 'Corrected', 'Real filtered (arduino)','Corrected filtered (arduino)' )

    pd_realValue_generic = fitdist(realValue_generic,'Normal');
    pd_correctedValue_generic = fitdist(correctedValue_generic,'Normal');
    pd_realValueFiltered_generic = fitdist(realValueFiltered_generic,'Normal');
    pd_correctedValueFiltered_generic = fitdist(correctedValueFiltered_generic,'Normal');
    
    deltamu_realValue_generic =                 pd_realValue_generic.mu - nominalValue;
    deltamu_correctedValue_generic =            pd_correctedValue_generic.mu - nominalValue ;
    deltamu_realValueFiltered_generic =         pd_realValueFiltered_generic.mu - nominalValue;
    deltamu_correctedValueFiltered_generic =    pd_correctedValueFiltered_generic.mu - nominalValue;
    
    x_values = linspace(x_min, x_max, 500);

    pdf_realValue_generic = pdf(pd_realValue_generic,x_values);
    pdf_correctedValue_generic =  pdf(pd_correctedValue_generic,x_values);
    pdf_realValueFiltered_generic = pdf(pd_realValueFiltered_generic,x_values);
    pdf_correctedValueFiltered_generic =  pdf(pd_correctedValueFiltered_generic,x_values);
    

figure
    plot(x_values, pdf_realValue_generic)
    hold on
    plot(x_values, pdf_correctedValue_generic)
    plot(x_values, pdf_realValueFiltered_generic)
    plot(x_values, pdf_correctedValueFiltered_generic)
    YLim = ylim;
    plot([nominalValue, nominalValue], YLim, 'k--')
%     plot([nominalValue-5, nominalValue-5], YLim, 'k--', 'HandleVisibility', 'off')
%     plot([nominalValue+5, nominalValue+5], YLim, 'k--', 'HandleVisibility', 'off')
    
    grid on
    legend( sprintf('Real (\\Delta\\mu=%.3f)', deltamu_realValue_generic), ...
            sprintf('Corrected (\\Delta\\mu=%.3f)', deltamu_correctedValue_generic), ...
            sprintf('Real filtered (arduino) (\\Delta\\mu=%.3f)', deltamu_realValueFiltered_generic), ...
            sprintf('Corrected filtered (arduino) (\\Delta\\mu=%.3f)', deltamu_correctedValueFiltered_generic), ...
            sprintf('Nominal value'))
            

figure
    histogram(realValueWU_generic, linspace(min(realValueWU_generic), max(realValueWU_generic), 20),'Normalization','pdf')
    hold on 
    histogram(OFFSET_generic, linspace(min(OFFSET_generic), max(OFFSET_generic), 20),'Normalization','pdf')
    grid on
    title('Histogram measurement WU')
% figure
%     scatter(realValue_generic, realValueWU_generic, [], time_generic, 'o')
%     hold on
%     grid on
%     scatter(realValue_generic, OFFSET_generic, [], time_generic, '+')
    
  
%% Vcc

figure
subplot(2, 1, 1)

    plotyy(time_generic, Vcc_generic, time_generic, realValue_generic)
    hold on

%     '--', 'LineWidth', 3
%     'DisplayName', 'Corrected Filt Arduino', 'Marker', 'o', 'LineStyle', '--')
 
    grid on

subplot(2, 1, 2)
    histogram(Vcc_generic)
    hold on
    grid on

%% Complete analysis 

cmoAnalysisData = realValueFiltered_generic;
pd_generic = fitdist(cmoAnalysisData,'Normal');


x_min = min( [ cmoAnalysisData ]);
x_max = max( [ cmoAnalysisData ]);

x_min = floor(x_min);
x_max = ceil(x_max);

x_values = linspace(x_min, x_max, 500);

pdf_generic_distribution = pdf(pd_generic,x_values);

figure
subplot(2, 1, 1)
    plot(x_values, pdf_generic_distribution, 'DisplayName', 'Normal distribution')
    hold on
    histogram(cmoAnalysisData, 'Normalization','pdf')
    YLim = ylim;
    plot([nominalValue, nominalValue], YLim, 'k--')
    plot([nominalValue-5, nominalValue-5], YLim, 'k--')
    plot([nominalValue+5, nominalValue+5], YLim, 'k--')
    legend show
    grid on
    title(sprintf('Report of ''%s''', regexprep(filename, '_', ' ')))

nominalValueVector = nominalValue*ones(size(time_generic));
subplot(2, 1, 2)
    plot(time_generic, realValue_generic, '--', 'DisplayName', 'Real',  'LineWidth', 2);                 
    hold on
    plot(time_generic, correctedValue_generic, 'DisplayName', 'Corrected');            
    plot(time_generic, realValueFiltered_generic, 'DisplayName', 'Real Filt Arduino', 'Marker', 'x', 'LineStyle', '--')
    plot(time_generic, correctedValueFiltered_generic, 'DisplayName', 'Corrected Filt Arduino', 'Marker', 'o', 'LineStyle', '--')
 
    plot(time_generic, nominalValue*ones(size(time_generic)), 'k--', 'HandleVisibility', 'off')
    plot(time_generic, (nominalValue-5)*ones(size(time_generic)), 'k--', 'HandleVisibility', 'off')
    plot(time_generic, (nominalValue+5)*ones(size(time_generic)), 'k--', 'HandleVisibility', 'off')
    grid on
    legend show

    
% 	errReal =                   immse(nominalValueVector,realValue_generic);
% 	errCorrected =              immse(nominalValueVector,correctedValue_generic);
% 	errCorrectedFiltArduino =   immse(nominalValueVector,realValueFiltered_generic);
% 	errRealFilt =               immse(nominalValueVector,realValue_generic_filt);
% 	errCorrectedFilt =          immse(nominalValueVector,correctedValue_generic_filt);
    

%% Sandbox

[bincounts,bincenters]=hist(cmoAnalysisData,ceil(sqrt(numel(cmoAnalysisData))));
binlimits = [bincenters-(bincenters(2)-bincenters(1))/2, bincenters(end)+(bincenters(2)-bincenters(1))/2, ];



  figure
    plot(x_values, pdf_generic_distribution, 'DisplayName', '1s')
    hold on
    histogram(cmoAnalysisData, binlimits , 'Normalization', 'pdf')
%     histogram(cmoAnalysisData, x_values(1:25:500) , 'Normalization', 'pdf')
%     hold on
%     histogram(cmoAnalysisData, x_values(1:50:500) , 'Normalization', 'pdf')
%     histogram(cmoAnalysisData, x_values(1:10:500) , 'Normalization', 'pdf')
%     histogram(cmoAnalysisData, x_values(1:2:500) , 'Normalization', 'pdf')
    
    figure
    histfit(cmoAnalysisData, ceil(sqrt(numel(cmoAnalysisData))))
    
    
[bincounts,bincenters]=hist(cmoAnalysisData,ceil(sqrt(numel(cmoAnalysisData))));