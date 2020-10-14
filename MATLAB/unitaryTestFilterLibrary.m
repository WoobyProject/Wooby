

filedir = '/Users/macretina/Documents/Humanity Lab/Wooby/MATLAB/datasets/Filter';
filename = 'filter_try1.csv';
% filename = 'filter_try_doubleTs.csv';
% filename = 'filter_try_halfTs.csv';

M = csvread(fullfile(filedir,filename));


%% 

    time = M(:,1)/1000; % in s
    arduinoInput = M(:,2);
    arduinoFiltered = M(:,3);
  
%%

Ts_real = mean(diff(time));

tau = 2;
myFilter = ss(-1/tau, 1/tau, 1, 0);
myFilterDisc = c2d(myFilter, Ts_real);

time_calc = linspace(time(1), time(end), length(time));

matlabFiltered = lsim(myFilter, arduinoInput, time_calc);
matlabFilteredDisc = lsim(myFilterDisc, arduinoInput, time_calc);

% figure
% plot(time, time)
% hold on
% plot(time, time_calc)

%% Plot

    figure
    plot(time, arduinoInput, '--', 'DisplayName', 'Input')
    hold on
    plot(time, arduinoFiltered, 's--', 'DisplayName', 'Arduino')
    plot(time, matlabFiltered, '*--', 'DisplayName', 'Matlab Cont')
    plot(time, matlabFilteredDisc, '*--', 'DisplayName', 'Matlab Disc')
    legend show
    grid on
    
    
    figure
    plot(time, arduinoFiltered-matlabFiltered, '--', 'DisplayName', 'Error Cont.')
    hold on 
    plot(time, arduinoFiltered-matlabFilteredDisc, '--', 'DisplayName', 'Error Discrte')
    
    grid on
    