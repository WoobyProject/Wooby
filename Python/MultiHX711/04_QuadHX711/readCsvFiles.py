import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import glob

subset = "WoobyQuadHX711ForTest"
folder = "C:/Users/pasca/Wooby/devs/Python/datasets/" + subset
csv_files = glob.glob(os.path.join(folder, "*.csv"))
measures = pd.DataFrame()
#weights = [0, 993, 1981, 2966, 3956, 4944, 5939, 6932, 7923, 8914, 9910]
weights = []
i = 0
j = 1
for file_name in csv_files :
    lweight = file_name.split("_")
    weight = int(lweight[1][:-2])
    if not(weight in weights) :
        weights.append(weight)
weights.sort()
fig, ax = plt.subplots()
for weight in weights :
    for j in range(0,5) :
        file_name = "{}/{}_{}gr_{}.csv".format(folder, subset, weight, j+1)
        print(file_name)
        measures = pd.read_csv(file_name, low_memory=False)
        x = []
        y1 = []
        y2 = []
        y3 = []
        y4 = []
        for measure in measures["relativeVal_WU1"] :
            x.append(weight)
            y1.append(measure)
        for measure in measures["relativeVal_WU2"] :
            y2.append(measure)
        for measure in measures["relativeVal_WU3"] :
            y3.append(measure)
        for measure in measures["relativeVal_WU4"] :
            y4.append(measure)
        if i == 0 and j == 1 :
            ax.scatter(x, y1, c="blue", label="Sensor #1")
            ax.scatter(x, y2, c="red", label="Sensor #2")
            ax.scatter(x, y3, c="green", label="Sensor #3")
            ax.scatter(x, y4, c="orange", label="Sensor #4")
        else :
            ax.scatter(x, y1, c="blue")
            ax.scatter(x, y2, c="red")
            ax.scatter(x, y3, c="green")
            ax.scatter(x, y4, c="orange")
    i = i + 1
ax.legend()
plt.grid(True, axis="both")
plt.show()
