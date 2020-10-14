%%%% Gyro study %%%%

    filedir = '/Users/macretina/Documents/Humanity Lab/Wooby/MATLAB/datasets/study_Wooby_GY';
    filename = 'WoobyGY_data_7ms_1010gr_BAT.csv';
%     filename = 'WoobyGY_data_7ms_0gr_BAT.csv';
%     filename = 'WoobyGY_data_7ms_1010gr_BAT2.csv';
%     filename = 'WoobyGY_data_7ms_0gr_movingHanging.csv';
%     filename = 'WoobyGY_data_7ms_0gr_BATCH.csv';
    filename = 'WoobyGY_data_7ms_500gr_BAT.csv';
    filename = 'WoobyGY_data_7ms_500gr_BAT_hanging.csv';
    filename = 'WoobyGY_data_7ms_9580gr_BAT_hanging.csv';
    filename = 'WoobyGY_data_7ms_500gr_BAT_hanging_oscil.csv';
    filename = 'WoobyGY_data_7ms_500gr_BAT_hanging_static.csv';
    
    filename = 'WoobyGY_data_7ms_500gr_BAT_hanging_bilateral.csv';
     
    
    
    filedir = '/Users/macretina/Documents/Humanity Lab/Wooby/MATLAB/datasets/Wooby_v1';
    filename = 'Wooby_v1_data_7ms_1422gr_hanging_test.csv';

    
    myWoobyGYdata = readWoobyData(filedir,filename);
  
%     myWoobyGYdata.phi =   myWoobyGYdata.phi   - mean(myWoobyGYdata.phi(myWoobyGYdata.time>900));
%     myWoobyGYdata.theta = myWoobyGYdata.theta - mean(myWoobyGYdata.theta(myWoobyGYdata.time>900));


%     myWoobyGYdata.phi =   myWoobyGYdata.phi   + 1.45;
%     myWoobyGYdata.theta = myWoobyGYdata.theta - 6.00;

%%


figure
    plot(myWoobyGYdata.time, myWoobyGYdata.nominalValueVec, '--', 'Color', [0.5,0.5,0.5] )
    hold on
    plot(myWoobyGYdata.time, myWoobyGYdata.realValue)
    plot(myWoobyGYdata.time, myWoobyGYdata.correctedValueFiltered)
    
    plot(myWoobyGYdata.time, myWoobyGYdata.correctedValueFiltered ./( cosd(myWoobyGYdata.thetaFiltered) .* cosd(myWoobyGYdata.phiFiltered))  )
    
    
    plot(myWoobyGYdata.time, myWoobyGYdata.nominalValueVec+5, '--', 'Color', [0.5,0.5,0.5], 'HandleVisibility', 'off')
    plot(myWoobyGYdata.time, myWoobyGYdata.nominalValueVec-5, '--', 'Color', [0.5,0.5,0.5], 'HandleVisibility', 'off')
    
    grid on  
	ylabel('Comp')
    legend('Nominal', 'Raw data','Corrected value filt.', 'Corrected with angles')
 
figure
    plot(myWoobyGYdata.time, myWoobyGYdata.theta)
    hold on
    plot(myWoobyGYdata.time, myWoobyGYdata.phi)
    
    plot(myWoobyGYdata.time, myWoobyGYdata.thetaFiltered, '--')
    hold on
    plot(myWoobyGYdata.time, myWoobyGYdata.phiFiltered, '--')
    grid on
    legend('Theta', 'Phi')
        
    %%
figure
    plot(myWoobyGYdata.time, (180/pi)*acos(1./(myWoobyGYdata.realValue./myWoobyGYdata.nominalValueVec)))
    grid on
    hold on
    
    plot(myWoobyGYdata.time, myWoobyGYdata.theta)
%     xlim([492, 506])
    
figure
    myfft(myWoobyGYdata.time, myWoobyGYdata.realValue)
    


    