%% %% Vcc study %%%%

% 0 gr

    filedir = '/Users/macretina/Documents/Humanity Lab/Wooby/MATLAB/datasets/study_Vcc';
    filename = 'Vcc_data_7ms_0gr_BAT.csv';
    data0grBAT = readWoobyData(filedir,filename);
    
    filedir = '/Users/macretina/Documents/Humanity Lab/Wooby/MATLAB/datasets/study_Vcc';
    filename = 'Vcc_data_7ms_0gr_NOBAT.csv';
    data0grNOBAT = readWoobyData(filedir,filename);

% 1000 gr

    filedir = '/Users/macretina/Documents/Humanity Lab/Wooby/MATLAB/datasets/study_Vcc';
    filename = 'Vcc_data_7ms_1000gr_BAT.csv';
    data1000grBAT = readWoobyData(filedir,filename);
    
    filedir = '/Users/macretina/Documents/Humanity Lab/Wooby/MATLAB/datasets/study_Vcc';
    filename = 'Vcc_data_7ms_1000gr_NOBAT.csv';
    data1000grNOBAT = readWoobyData(filedir,filename);

% 1500 gr

    filedir = '/Users/macretina/Documents/Humanity Lab/Wooby/MATLAB/datasets/study_Vcc';
    filename = 'Vcc_data_7ms_1500gr_BAT.csv';
    data1500grBAT = readWoobyData(filedir,filename);
    
    filedir = '/Users/macretina/Documents/Humanity Lab/Wooby/MATLAB/datasets/study_Vcc';
    filename = 'Vcc_data_7ms_1500gr_NOBAT.csv';
    data1500grNOBAT = readWoobyData(filedir,filename);
    
%%


figure
    plot(  data0grBAT.timeNorm,   data0grBAT.erroRealValue, 'DisplayName',   data0grBAT.filename)
    hold on
    plot(data0grNOBAT.timeNorm, data0grNOBAT.erroRealValue, 'DisplayName', data0grNOBAT.filename)
    plot(  data1000grBAT.timeNorm,   data1000grBAT.erroRealValue,  'DisplayName',   data1000grBAT.filename)
    plot(data1000grNOBAT.timeNorm, data1000grNOBAT.erroRealValue,  'DisplayName', data1000grNOBAT.filename)
    
    grid on
    legend show
    

figure
    scatter(  data0grBAT.realValue,   data0grBAT.realValueWU, data0grBAT.Vcc, 'DisplayName',   data0grBAT.filename)
    hold on
    scatter(data0grNOBAT.realValue, data0grNOBAT.realValueWU, data0grBAT.Vcc, 'DisplayName', data0grNOBAT.filename)
    
    scatter(  data1000grBAT.realValue,   data1000grBAT.realValueWU,   data1000grBAT.Vcc, 'DisplayName',   data1000grBAT.filename)
    scatter(data1000grNOBAT.realValue, data1000grNOBAT.realValueWU, data1000grNOBAT.Vcc, 'DisplayName', data1000grNOBAT.filename)
    
    grid on
    legend show
    ylabel('Output(wu)')
    xlabel('Real weight (gr)')
    title('Offset behaviour')
    
    
figure
    scatter(data0grBAT.erroRealValue,       data0grBAT.Vcc,     'DisplayName',   data0grBAT.filename)
    hold on
    scatter(data0grNOBAT.erroRealValue,     data0grNOBAT.Vcc,   'DisplayName',   data0grBAT.filename)
    scatter(data1000grBAT.erroRealValue,    data1000grBAT.Vcc,  'DisplayName',   data0grBAT.filename)
    scatter(data1000grNOBAT.erroRealValue,  data1000grNOBAT.Vcc,'DisplayName',   data0grBAT.filename)
    
    grid on
    legend show
    xlabel('Error to nominal value (gr)')
    ylabel('Vcc (V)')

    
%%     

figure
% scatter (     data0grNOBAT.Vcc,    data0grNOBAT.realValueWU -      data0grBAT.meanrealValueWU , 'DisplayName', 'O gr',  'MarkerFaceColor', 'red' , 'MarkerEdgeColor','red')
hold on
scatter (     data0grNOBAT.meanVcc,    data0grNOBAT.meanrealValueWU -      data0grBAT.meanrealValueWU, 200, 'x',  'MarkerFaceColor', 'red' , 'MarkerEdgeColor','red')
hold on

% scatter (     data0grBAT.Vcc,    data0grBAT.realValueWU -      data0grBAT.meanrealValueWU , 'DisplayName', 'O gr',  'MarkerFaceColor', 'red' , 'MarkerEdgeColor','red')
scatter (     data0grBAT.meanVcc,    data0grBAT.meanrealValueWU -      data0grBAT.meanrealValueWU , 200, 'x',  'MarkerFaceColor', 'red' , 'MarkerEdgeColor','red')
hold on

% 1000 gr
% scatter (     data1000grNOBAT.Vcc,    data1000grNOBAT.realValueWU -      data1000grBAT.meanrealValueWU , 'DisplayName', 'O gr',  'MarkerFaceColor', 'blue' , 'MarkerEdgeColor','blue')
hold on
scatter (     data1000grNOBAT.meanVcc,    data1000grNOBAT.meanrealValueWU -      data1000grBAT.meanrealValueWU, 200, 'x',  'MarkerFaceColor', 'blue' , 'MarkerEdgeColor','blue')
hold on

% scatter (     data1000grBAT.Vcc,    data1000grBAT.realValueWU -      data1000grBAT.meanrealValueWU , 'DisplayName', 'O gr',  'MarkerFaceColor', 'blue' , 'MarkerEdgeColor','blue')
scatter (     data1000grBAT.meanVcc,    data1000grBAT.meanrealValueWU -      data1000grBAT.meanrealValueWU , 200, 'x',  'MarkerFaceColor', 'blue' , 'MarkerEdgeColor','blue')
hold on



% 1500 gr
% scatter (     data1500grNOBAT.Vcc,    data1500grNOBAT.realValueWU -      data1500grBAT.meanrealValueWU , 'DisplayName', 'O gr',  'MarkerFaceColor', 'green' , 'MarkerEdgeColor','green')
hold on
scatter (     data1500grNOBAT.meanVcc,    data1500grNOBAT.meanrealValueWU -      data1500grBAT.meanrealValueWU, 200, 'x',  'MarkerFaceColor', 'green' , 'MarkerEdgeColor','green')
hold on

% scatter (     data1500grBAT.Vcc,    data1500grBAT.realValueWU -      data1500grBAT.meanrealValueWU , 'DisplayName', 'O gr',  'MarkerFaceColor', 'green' , 'MarkerEdgeColor','green')
scatter (     data1500grBAT.meanVcc,    data1500grBAT.meanrealValueWU -      data1500grBAT.meanrealValueWU , 200, 'x',  'MarkerFaceColor', 'green' , 'MarkerEdgeColor','green')
hold on




grid on
    ylabel('Delta raw measure (wu)')
    xlabel('Vcc (V)')
%% 
    
    figure
    scatter3(data0grBAT.Vcc,    data0grBAT.realValueWU*0 + 0,         data0grBAT.realValueWU)
    hold on
    scatter3(data1000grBAT.Vcc, data1000grBAT.realValueWU*0 + 1000,   data1000grBAT.realValueWU)
    scatter3(data1500grBAT.Vcc, data1500grBAT.realValueWU*0 + 1500,   data1500grBAT.realValueWU)
    
    scatter3(data0grNOBAT.Vcc,    data0grNOBAT.realValueWU*0 + 0,         data0grNOBAT.realValueWU)
    hold on
    scatter3(data1000grNOBAT.Vcc, data1000grNOBAT.realValueWU*0 + 1000,   data1000grNOBAT.realValueWU)
    scatter3(data1500grNOBAT.Vcc, data1500grNOBAT.realValueWU*0 + 1500,   data1500grNOBAT.realValueWU)
    
    
    xlabel('Vcc (V)')
    ylabel('Real weight (gr)')
    zlabel('WU measure (wu)')
    view([1 0 0 ])
    
%%

Vcc_vec = [4.6, 5];
delta_OFFSET = [-650, 0];

P_Vcc = polyfit(Vcc_vec, delta_OFFSET,1);

m = P_Vcc(1);
b = P_Vcc(2);