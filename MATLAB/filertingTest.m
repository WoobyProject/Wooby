%% Filtering Unitary Test

filedir = '/Users/macretina/Documents/Humanity Lab/Baby Scale/datasets/Ursa_Major';
filename = 'UMajor_data_10ms_0gr_1.csv';


M = csvread(fullfile(filedir,filename));


% Nominal value
    iStr = regexp(filename, '_'); iStr = iStr(2)+1;
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

% Calculation 
    diffMeasure_generic = afterMeasure_generic-beforeMeasure_generic;
    meandiffMeasure_generic = mean(diffMeasure_generic);
    ndata_generic = length(time_generic);
    timeMeasure = (time_generic(end)-time_generic(1));

%% Filter equation analysis

Te = 0.1;

tau = 10;
myFilter = ss(-1/tau, 1/tau, 1, 0);

Ts = 0.1;

myFilterDisc_zoh= c2d(myFilter, Te , 'zoh');
myFilterDisc_foh= c2d(myFilter, Te , 'foh');
myFilterDisc_tustin = c2d(myFilter, Te , 'tustin');

%      a
%   --------
%    z - b

myFilterDisc_calc = tf(1-exp(-Ts/tau),[1, -exp(-Ts/tau)],Ts);
% Check http://web.cecs.pdx.edu/~tymerski/ece452/6.pdf
Tsim = 10*Te; %5*tau;
figure
step(myFilter, Tsim)
hold on
step(myFilterDisc_zoh, Tsim, 'r-')
step(myFilterDisc_foh, Tsim, 'b-')
step(myFilterDisc_tustin, Tsim, 'g--')
step(myFilterDisc_calc, Tsim, 'y--')

grid on
legend show
% myFilterDisc2 = myFilterDisc*tf([1 100], [1], Te) 
% dcgain(myFilterDisc2)
% myFilterDisc2 = myFilterDisc2/ans
% step(myFilterDisc2)

%% Filtering try

tau = 15;
myFilter = ss(-1/tau, 1/tau, 1, 0);

% myFilter2 = myFilter*tf([1 2/(tau)], 1);
% dcgain(myFilter2)
% myFilter2 = myFilter2/ans;
% 
% figure
% step(myFilter, myFilter2)

% time_generic_calc = (time_generic - time_generic(1));
% time_generic_calc = linspace(0, time_generic_calc(end), length(time_generic_calc));
time_generic_calc = linspace(time_generic(1), time_generic(end), length(time_generic));
% figure
% plot(time_generic, time_generic-time_generic(1))
% hold on
% plot(time_generic, time_generic_calc)
% 
% figure
% plot(time_generic, time_generic_calc'-(time_generic-time_generic(1)) )

Te = time_generic_calc(2)-time_generic_calc(1);
myFilterDisc = c2d(myFilter, Te , 'zoh');

realValue_generic_filt =        lsim(myFilterDisc, realValue_generic,       time_generic_calc, realValue_generic(1));
correctedValue_generic_filt =   lsim(myFilterDisc, correctedValue_generic,  time_generic_calc, correctedValue_generic(1));

% figure
% step(myFilterDisc)
% hold on
% myFilterDisc2 = myFilterDisc*tf([1 100], [1], Te) 
% dcgain(myFilterDisc2)
% myFilterDisc2 = myFilterDisc2/ans
% step(myFilterDisc2)



  
%% Plots

x_min = min( realValue_generic );
x_max = max( realValue_generic );
x_min = floor(x_min);
x_max = ceil(x_max);


figure
    plot(time_generic, realValue_generic, '--', 'LineWidth', 1, 'DisplayName', 'Real')
    hold on
    plot(time_generic, correctedValue_generic,                  'DisplayName', 'Corrected')
    plot(time_generic, realValueFiltered_generic,               'DisplayName', 'Real filtered (arduino)')
    plot(time_generic, correctedValueFiltered_generic,          'DisplayName', 'Corrected filtered (arduino)')
%     plot(time_generic_calc, realValue_generic_filt, 'LineWidth', 3, 'DisplayName', 'Real filtered (Matlab)')
    
    grid on
    legend show

    
figure
    myfft(time_generic, realValue_generic);
    hold on
    myfft(time_generic, correctedValueFiltered_generic);
    myfft(time_generic_calc, realValue_generic_filt);
    legend('Real','Corrected filtered (arduido)', 'Real filtered (Matlab) ')
    
figure
    histogram(realValue_generic, linspace(x_min, x_max, 20),'Normalization','pdf')
    hold on
    histogram(correctedValue_generic, linspace(x_min, x_max, 20),'Normalization','pdf')
    histogram(realValueFiltered_generic, linspace(x_min, x_max, 20),'Normalization','pdf')
    histogram(correctedValueFiltered_generic, linspace(x_min, x_max, 20),'Normalization','pdf')
    grid on
    legend('Real', 'Corrected', 'Real filtered (arduino)','Corrected filtered (arduino)' )

    pd_realValue_generic = fitdist(realValue_generic,'Normal')
    pd_correctedValue_generic = fitdist(correctedValue_generic,'Normal')
    pd_realValueFiltered_generic = fitdist(realValueFiltered_generic,'Normal')
    pd_correctedValueFiltered_generic = fitdist(correctedValueFiltered_generic,'Normal')
    

x_values = linspace(x_min, x_max, 100);

    pdf_realValue_generic =                 pdf(pd_realValue_generic,               x_values);
    pdf_correctedValue_generic =            pdf(pd_correctedValue_generic,          x_values);
    pdf_realValueFiltered_generic =         pdf(pd_realValueFiltered_generic,       x_values);
    pdf_correctedValueFiltered_generic =    pdf(pd_correctedValueFiltered_generic,  x_values);

figure
    plot(x_values, pdf_realValue_generic)
    hold on
    plot(x_values, pdf_correctedValue_generic)
    plot(x_values, pdf_realValueFiltered_generic)
    plot(x_values, pdf_correctedValueFiltered_generic)
    
    grid on
    legend('Real', 'Corrected', 'Real filtered (arduino)','Corrected filtered (arduino)' )


    
%% Analysis all histograms

pd_generic = fitdist(realValue_generic,'Normal');

x_min = min( [ realValue_generic ]);
x_max = max( [ realValue_generic ]);

x_min = floor(x_min);
x_max = ceil(x_max);

x_values = linspace(x_min, x_max, 100);

pdf_generic = pdf(pd_generic,x_values);


figure
subplot(2, 1, 1)
    plot(x_values, pdf_generic, 'DisplayName', '1s')
    hold on
    histogram(realValue_generic,'Normalization','pdf')
    YLim = ylim;
    plot([nominalValue, nominalValue], YLim, 'k--')
    plot([nominalValue-5, nominalValue-5], YLim, 'k--')
    plot([nominalValue+5, nominalValue+5], YLim, 'k--')
    legend show
    grid on

nominalValueVector = nominalValue*ones(size(time_generic));
subplot(2, 1, 2)
    plot(time_generic, realValue_generic, '--', 'DisplayName', 'Real',  'LineWidth', 2);                 
    hold on
    plot(time_generic, correctedValue_generic, 'DisplayName', 'Corrected');            
    plot(time_generic, realValueFiltered_generic, 'DisplayName', 'Real Filt Arduino', 'Marker', 'o', 'LineStyle', '--')
%     plot(time_generic, realValue_generic_filt, 'DisplayName', 'Real Filt', 'Marker', 'x', 'LineStyle', '--');            
%     p = plot(time_generic, correctedValue_generic_filt, 'DisplayName', 'Corrected Filt', 'Marker', '+', 'LineStyle', '--');  
    plot(time_generic, nominalValue*ones(size(time_generic)), 'k--', 'HandleVisibility', 'off')
    plot(time_generic, (nominalValue-5)*ones(size(time_generic)), 'k--', 'HandleVisibility', 'off')
    plot(time_generic, (nominalValue+5)*ones(size(time_generic)), 'k--', 'HandleVisibility', 'off')
    grid on
    legend show

    
	errReal =                   immse(nominalValueVector,realValue_generic);
	errCorrected =              immse(nominalValueVector,correctedValue_generic);
	errCorrectedFiltArduino =   immse(nominalValueVector,realValueFiltered_generic);
	errRealFilt =               immse(nominalValueVector,realValue_generic_filt);
	errCorrectedFilt =          immse(nominalValueVector,correctedValue_generic_filt);
    
    