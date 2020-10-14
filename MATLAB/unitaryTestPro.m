
%%%% Wooby v1 %%%%

    filedir = '/Users/macretina/Documents/Humanity Lab/Wooby/MATLAB/datasets/Wooby_v1';

    % filename = 'CALIB_Wooby_v1_data_10ms_0gr_1.csv';
    % filename = 'CALIB_Wooby_v1_data_10ms_503gr_1.csv';
    % filename = 'CALIB_Wooby_v1_data_10ms_1009gr_1.csv';
    % filename = 'CALIB_Wooby_v1_data_10ms_1513gr_1.csv';

    % filename = 'Wooby_v1_data_10ms_1000gr_1.csv';
    % filename = 'Wooby_v1_data_10ms_1000gr_moving.csv';

    filename = 'Wooby_v1_data_7ms_10gr_hanging_test.csv';
    
    
    myWoobyTestdata = readWoobyData(filedir,filename);
    
    
%%
    
    
figure

subplot(2, 1, 1)
    plot(myWoobyTestdata.time, myWoobyTestdata.nominalValueVec, '--', 'Color', [0.5,0.5,0.5], 'DisplayName', 'Nominal')
    hold on
    plot(myWoobyTestdata.time, myWoobyTestdata.realValue, 'DisplayName', 'Raw data')
    plot(myWoobyTestdata.time, myWoobyTestdata.correctedValueFiltered, 'DisplayName', 'Corrected value filt.')
    
    % plot(myWoobyTestdata.time, myWoobyTestdata.correctedValueFiltered ./( cosd(myWoobyTestdata.thetaFiltered) .* cosd(myWoobyTestdata.phiFiltered)), 'DisplayName', 'Corrected with angles')
    
    
    plot(myWoobyTestdata.time, myWoobyTestdata.nominalValueVec+5, '--', 'Color', [0.5,0.5,0.5], 'HandleVisibility', 'off')
    plot(myWoobyTestdata.time, myWoobyTestdata.nominalValueVec-5, '--', 'Color', [0.5,0.5,0.5], 'HandleVisibility', 'off')
    
    grid on  
	ylabel('Comp')
    legend show
 
subplot(2, 1, 2)
    plot(myWoobyTestdata.time, myWoobyTestdata.theta, 'DisplayName', '\theta')
    hold on
    plot(myWoobyTestdata.time, myWoobyTestdata.phi, 'DisplayName', '\phi')
    
    plot(myWoobyTestdata.time, myWoobyTestdata.thetaFiltered, '--', 'DisplayName', '\theta_{filt}')
    hold on
    plot(myWoobyTestdata.time, myWoobyTestdata.phiFiltered, '--', 'DisplayName', '\theta_{filt}')
    grid on
    
    plot(myWoobyTestdata.time, myWoobyTestdata.time*0+10, '--', 'Color', [0.5,0.5,0.5], 'HandleVisibility', 'off')
    plot(myWoobyTestdata.time, myWoobyTestdata.time*0-10, '--', 'Color', [0.5,0.5,0.5], 'HandleVisibility', 'off')
    
    
    legend show
