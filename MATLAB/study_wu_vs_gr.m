%% For prototype 1: Osa Menor

realWeight = [0,        0.504,      1.009,  1.513,	2.010,	2.513]*1000;
WU =         [-66679, -47104, -24951, -4352,  17687, 35066];

P = polyfit(realWeight, WU,1);
ep = 0.02; %error percentage at real zero = 0 gr

OFFSET1 = P(2);
SCALE1 = P(1);

figure
    plot(realWeight, WU)
    hold on 
    plot(realWeight,     P(1)*realWeight+P(2))
    plot(realWeight, (1-ep)*P(1)*realWeight+P(2), '--')
    plot(realWeight, (1+ep)*P(1)*realWeight+P(2), '--')
    ylabel('Output(wu)')
    xlabel('Real weight')
    title('Offset behaviour')
    grid on
    legend('Real data', 'Polyfit', 'Location', 'best')



%% For prototype 2: Osa Mayor

realWeight = [0,        0.504,      1.009,  1.513,	2.010,	2.513]*1000;
WU =         [46541,    25087,      3611,	-17820,	-38867,	-60294];


P = polyfit(realWeight, WU,1);
ep = 0.02; %error percentage at real zero = 0 gr

OFFSET2 = P(2);
SCALE2 = P(1);

figure
    plot(realWeight, WU)
    hold on 
    plot(realWeight,     P(1)*realWeight+P(2))
    % plot(realWeight, (1-ep)*P(1)*realWeight+P(2), '--')
    % plot(realWeight, (1+ep)*P(1)*realWeight+P(2), '--')
    ylabel('Output(wu)')
    xlabel('Real weight')
    title('Offset behaviour')
    grid on
    legend('Real data', 'Polyfit', 'Location', 'best')

%% For prototype 3: Wooby v1

realWeight = [0,                   0.504,             1.009,           1.513]*1000;
WU =         [6.0011e+03,    -2.5068e+04,       -5.6323e+04,     -8.7483e+04];

P = polyfit(realWeight, WU,1);
ep = 0.02; %error percentage at real zero = 0 gr

OFFSET2 = P(2);
SCALE2 = P(1);


figure
    plot(realWeight, WU)
    hold on 
    plot(realWeight,     P(1)*realWeight+P(2))
    % plot(realWeight, (1-ep)*P(1)*realWeight+P(2), '--')
    % plot(realWeight, (1+ep)*P(1)*realWeight+P(2), '--')
    ylabel('Output(wu)')
    xlabel('Real weight')
    title('Offset behaviour')
    grid on
    legend('Real data', 'Polyfit', 'Location', 'best')

%% For prototype 4: Wooby v2 (colorful)


realWeight = [0,                   0.503,             1.009,           1.513]*1000;
filedir = '/Users/macretina/Documents/Humanity Lab/Wooby/MATLAB/datasets/Wooby_v2';
fileNames = {   'CALIB_Wooby_v2_data_10ms_0gr_1';
                'CALIB_Wooby_v2_data_10ms_503gr_1';
                'CALIB_Wooby_v2_data_10ms_1009gr_1';
                'CALIB_Wooby_v2_data_10ms_1513gr_1';
                } ;
            
WU =         [-62201.00,    -42429.00,       -24488.00,     -3399.00];


P = polyfit(realWeight, WU,1);
ep = 0.02; %error percentage at real zero = 0 gr

OFFSET2 = P(2);
SCALE2 = P(1);

figure
plot(realWeight, WU)
hold on 
plot(realWeight,     P(1)*realWeight+P(2))
% plot(realWeight, (1-ep)*P(1)*realWeight+P(2), '--')
% plot(realWeight, (1+ep)*P(1)*realWeight+P(2), '--')
ylabel('Output(wu)')
xlabel('Real weight')
title('Offset behaviour')
grid on
legend('Real data', 'Polyfit', 'Location', 'best')


%%

filedir = '/Users/macretina/Documents/Humanity Lab/Baby Scale/datasets/Ursa_Major';
filename = 'UMajor_data_10ms_0gr_1.csv';

M = csvread(fullfile(filedir,filename));
realValue_generic = M(:,2);
realValueWU_generic = M(:,12);

plot(realValue_generic, realValueWU_generic,'+');




filedir = '/Users/macretina/Documents/Humanity Lab/Baby Scale/datasets/Ursa_Major';
filename = 'UMajor_data_10ms_1513gr_1.csv';

M = csvread(fullfile(filedir,filename));
realValue_generic = M(:,2);
realValueWU_generic = M(:,12);

plot(realValue_generic, realValueWU_generic,'+');





filedir = '/Users/macretina/Documents/Humanity Lab/Baby Scale/datasets/Ursa_Major';
filename = 'UMajor_data_10ms_2513gr_1.csv';

M = csvread(fullfile(filedir,filename));
realValue_generic = M(:,2);
realValueWU_generic = M(:,12);

plot(realValue_generic, realValueWU_generic,'+');

