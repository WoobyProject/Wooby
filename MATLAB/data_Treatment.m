



%% 1 ms

filedir = '/Users/macretina/Documents/Humanity Lab/Wooby/MATLAB/datasets/_old_datasets';
filename = 'data_1ms.csv';
M = csvread(fullfile(filedir, filename));

time_1ms = M(:,1);
realValue_1ms = M(:,2);
correctedValue_1ms = M(:,3);
beforeMeasure_1ms = M(:,4);
afterMeasure_1ms = M(:,5);
diffMeasure_1ms = afterMeasure_1ms-beforeMeasure_1ms;
meandiffMeasure_1ms = mean(diffMeasure_1ms);
ndata_1ms = length(time_1ms);

%% Plots

figure
    plot(time_1ms, realValue_1ms, '--')
    hold on
    plot(time_1ms, correctedValue_1ms, '--')
    grid on


figure
    histogram(realValue_1ms)
    hold on
    histogram(correctedValue_1ms)
    grid on

figure
    plot(time_1ms, diffMeasure_1ms, '--')
    hold on
    grid on
    
%% 2 ms

filedir = '/Users/macretina/Documents/Humanity Lab/Wooby/MATLAB/datasets/_old_datasets';
filename = 'data_2ms.csv';
M = csvread(fullfile(filedir, filename));

time_2ms = M(:,1);
realValue_2ms = M(:,2);
correctedValue_2ms = M(:,3);
beforeMeasure_2ms = M(:,4);
afterMeasure_2ms = M(:,5);
diffMeasure_2ms = afterMeasure_2ms-beforeMeasure_2ms;
meandiffMeasure_2ms = mean(diffMeasure_2ms);
ndata_2ms = length(time_2ms);

%% Plots

figure
    plot(time_2ms, realValue_2ms, '--')
    hold on
    plot(time_2ms, correctedValue_2ms, '--')
    grid on


figure
    histogram(realValue_2ms)
    hold on
    histogram(correctedValue_2ms)
    grid on

figure
    plot(time_2ms, diffMeasure_2ms, '--')
    hold on
    grid on
    

%% 5 ms

filedir = '/Users/macretina/Documents/Humanity Lab/Wooby/MATLAB/datasets/_old_datasets';
filename = 'data_5ms.csv';
M = csvread(fullfile(filedir, filename));

time_5ms = M(:,1);
realValue_5ms = M(:,2);
correctedValue_5ms = M(:,3);
beforeMeasure_5ms = M(:,4);
afterMeasure_5ms = M(:,5);
diffMeasure_5ms = afterMeasure_5ms-beforeMeasure_5ms;
meandiffMeasure_5ms = mean(diffMeasure_5ms);
ndata_5ms = length(time_5ms);

%% Plots

figure
    plot(time_5ms, realValue_5ms, '--')
    hold on
    plot(time_5ms, correctedValue_5ms, '--')
    grid on


figure
    histogram(realValue_5ms)
    hold on
    histogram(correctedValue_5ms)
    grid on

figure
    plot(time_5ms, diffMeasure_5ms, '--')
    hold on
    grid on
        
%% 10 ms

filedir = '/Users/macretina/Documents/Humanity Lab/Wooby/MATLAB/datasets/_old_datasets';
filename = 'data_10ms.csv';
M = csvread(fullfile(filedir, filename));

time_10ms = M(:,1);
realValue_10ms = M(:,2);
correctedValue_10ms = M(:,3);
beforeMeasure_10ms = M(:,4);
afterMeasure_10ms = M(:,5);
diffMeasure_10ms = afterMeasure_10ms-beforeMeasure_10ms;
meandiffMeasure_10ms = mean(diffMeasure_10ms);
ndata_10ms = length(time_10ms);

%% Plots

figure
    plot(time_10ms, realValue_10ms, '--')
    hold on
    plot(time_10ms, correctedValue_10ms, '--')
    grid on


figure
    histogram(realValue_10ms)
    hold on
    histogram(correctedValue_10ms)
    grid on

figure
    plot(time_10ms, diffMeasure_10ms, '--')
    hold on
    grid on

    
    
%% 20 ms

filedir = '/Users/macretina/Documents/Humanity Lab/Wooby/MATLAB/datasets/_old_datasets';
filename = 'data_20ms.csv';
M = csvread(fullfile(filedir, filename));

time_20ms = M(:,1);
realValue_20ms = M(:,2);
correctedValue_20ms = M(:,3);
beforeMeasure_20ms = M(:,4);
afterMeasure_20ms = M(:,5);
diffMeasure_20ms = afterMeasure_20ms-beforeMeasure_20ms;
meandiffMeasure_20ms = mean(diffMeasure_20ms);
ndata_20ms = length(time_20ms);

%% Plots

figure
    plot(time_20ms, realValue_20ms, '--')
    hold on
    plot(time_20ms, correctedValue_20ms, '--')
    grid on

figure
    histogram(realValue_20ms)
    hold on
    histogram(correctedValue_20ms)
    grid on

figure
    plot(time_20ms, diffMeasure_20ms, '--')
    hold on
    grid on

    
%% Filtering try

% tau = 20;
% myFilter = tf(1, [tau 1]);
% 
% 
% for ii=[1 2 5 10 20]
%     eval(sprintf( 'time_%dms_calc = (time_%dms - time_%dms(1))/1000;', ii, ii, ii)) ;
%     % eval(sprintf( 'time_%dms_calc = 0:mean(diff(time_%dms_calc)):', ii, ii));
%     eval(sprintf( 'time_%dms_calc = linspace(0, time_%dms_calc(end), length(time_%dms_calc));', ii, ii, ii ) );
% end
% 
% 
% for ii=[1 2 5 10 20]
%     eval(sprintf('realValue_%dms_filt = lsim(myFilter, realValue_%dms, time_%dms_calc);', ii, ii, ii))
% end
% 
% figure
% for ii=[1 2 5 10 20]
% %     eval(sprintf('plot(time_%dms_calc, realValue_%dms,      ''DisplayName'', ''%dms'', ''LineStyle'', ''--'')', ii, ii, ii))
%     hold on
%     eval(sprintf('plot(time_%dms_calc, realValue_%dms_filt, ''DisplayName'', ''%dms'')', ii, ii, ii))
% end
% legend show


%% Analysis all histograms

pd_1ms = fitdist(realValue_1ms,'Normal');
pd_2ms = fitdist(realValue_2ms,'Normal');
pd_5ms = fitdist(realValue_5ms,'Normal');
pd_10ms = fitdist(realValue_10ms,'Normal');
pd_20ms = fitdist(realValue_20ms,'Normal');

x_min = min( [realValue_1ms;realValue_2ms;realValue_5ms;realValue_10ms;realValue_20ms ]);
x_max = max( [realValue_1ms;realValue_2ms;realValue_5ms;realValue_10ms;realValue_20ms ]);

x_min = floor(x_min);
x_max = ceil(x_max);

x_values = linspace(x_min, x_max, 100);

for ii=[1 2 5 10 20]
     eval(sprintf('pdf_%dms = pdf(pd_%dms,x_values);', ii, ii))
end

figure
for ii=[1 2 5 10 20]
       hold on
    eval(sprintf('plot(x_values, pdf_%dms, ''DisplayName'', ''%dms'')', ii, ii))
end
legend show
grid on

    
%% n Analysis

n_vec = [1 2 5 10 20];
means_vec = [meandiffMeasure_1ms, meandiffMeasure_2ms, meandiffMeasure_5ms, meandiffMeasure_10ms, meandiffMeasure_20ms];
measureTime_vec = means_vec./n_vec;


figure
    plot(n_vec,measureTime_vec, '+--' )
    grid on
    xlabel('Number of data by measurement (nMeasures) ')
    ylabel('Time/measurement (ms/mes)')
    title('Time per measurement (ms/mes)')
    
% p = polyfit(n_vec,measureTime_vec,1)

