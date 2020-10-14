


    filedir = '/Users/macretina/Documents/Humanity Lab/Wooby/MATLAB/datasets/study_GY';
    
    filename = 'GY_data_1.csv';
%     filename = 'GY_data_accelX.csv';
    
%     filename = 'GY_data_accelY.csv';
     
%     filename = 'GY_data_accelZ.csv';
    
    myGYdata = readGYdata(filedir,filename);
    
%%
    figure
    subplot(3, 1, 1)
        plot(myGYdata.time, myGYdata.Ax)
        grid on
        ylim([-1, 1])
        ylabel('Acc x')
    subplot(3, 1, 2)
        plot(myGYdata.time, myGYdata.Ay)
        grid on
        ylim([-1, 1])
        ylabel('Acc y')
    subplot(3, 1, 3)
        plot(myGYdata.time, myGYdata.Az)
        grid on
        ylim([-1, 1])
        ylabel('Acc z')