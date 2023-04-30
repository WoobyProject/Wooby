
import os
import re
import yaml

import random
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from sklearn.metrics import mean_squared_error

from typing import List

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression

from pyWooby.load import *

import seaborn as sns
import matplotlib.pyplot as plt

def extract_model_name(config_file_path):
    """
    Extracts the model name from the given configuration file path using regular expressions.

    Args:
        config_file_path (str): The path to the configuration file.

    Returns:
        str: The model name extracted from the configuration file path.
    """
    # Define the regular expression pattern to match the model name
    pattern = r"\/([\w\d]+)\/confModel.yaml"
    
    # Use the pattern to search for the model name in the configuration file path
    match = re.search(pattern, config_file_path)
    
    # Extract the model name from the match object
    model_name = match.group(1)
    
    # Return the model name
    return model_name


##########################        
#     Import functions   #
##########################


def createListForYMLfromFolder(folder_path):
    """
    Given a folder path, this function returns a list of all the weights of the CSV files
    found in the folder. The CSV files should be named in the format "WoobyTripleHX711ForTest3_Xgr_Y.csv", where X is the
    weight of the file in grams and Y is the run suffix.

    Args:
        folder_path (str): The path to the folder containing the CSV files.

    Returns:
        list: A list of weights (in grams) extracted from the file names.

    """
    
    
    weights = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".csv"):
            weight_match = re.search(r'(\d+)\s*gr', file_name)
            if weight_match:
                weight = int(weight_match.group(1))
                if weight not in weights:
                    weights.append(weight)

    weights.sort()
    
    return weights



def createYMLfromFolder(folder_path):
    """
    Given a folder path, this function creates a YML file and returns a list of all the weights of the CSV files
    found in the folder. The CSV files should be named in the format "WoobyTripleHX711ForTest3_Xgr_Y.csv", where X is the
    weight of the file in grams and Y is the run suffix.

    Args:
        folder_path (str): The path to the folder containing the CSV files.

    Returns:
        list: A list of weights (in grams) extracted from the file names.

    """
    weights = createListForYMLfromFolder(folder_path)

    with open(os.path.join(folder_path, 'weights.yml'), 'w') as f:
        yaml.dump({'weights': weights}, f)

    return weights


def readYMLdata(file_path):
    """
    Given a file path to a YML file, this function reads the file and returns the data contained within it as a Python
    dictionary.

    Args:
        file_path (str): The path to the YML file.

    Returns:
        dict: A dictionary containing the data read from the YML file.

    """
    with open(file_path, 'r') as f:
        data = yaml.safe_load(f)

    return data


def readYMLfile(file_path):
    """
    Given a file path to a YML file, this function reads the file and returns a dictionary with 
    the characteristics of the training on the YML file

    Args:
        file_path (str): The path to the YML file.

    Returns:
        list: A dictionary of the YML file

    """
    try:
        with open(file_path, 'r') as f:
            yml_data = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: file {file_path} not found.")
        return None
    except yaml.YAMLError as e:
        print(f"Error: {e}")
        return None
        
    return yml_data


def listFilesForTraining(file_path):
    """
    Given a file path to a YML file, this function reads the file and creates a list of files to be read based on the
    parameters specified in the YML file.

    If the value of ["dataset"]["type_read"] is "compact", then the function creates a list of files with the
    "file_suffix" + each value on "weights_list" and + all the numbers from 1 to the value of n_runs.

    Args:
        file_path (str): The path to the YML file.

    Returns:
        list: A list of file paths to be read.

    """
    
    yml_data = readYMLfile(file_path)

    
    if yml_data["dataset"]["type_read"] == "compact":
        file_suffix = yml_data["dataset"]["file_suffix"]
        weights_list = yml_data["dataset"]["weights_list"]
        n_runs = yml_data["dataset"]["n_runs"]

        files_to_read = []
        for weight in weights_list:
            for run in range(1, n_runs+1):
                file_name = f"{file_suffix}_{weight}gr_{run}.csv"
                file_path = os.path.join(yml_data["dataset"]["folder_path"], file_name)
                if os.path.isfile(file_path):
                    files_to_read.append(file_path)
                else:
                    print("File '{}' does not exist".format(file_path))

        return files_to_read
    else:
        raise ValueError(f"Unsupported type_read value: {yml_data['dataset']['type_read']}")
    
    
    
##############################        
#     PolyFeat functions     #
##############################



def trainWooby(configFile: str, dfTotal: pd.DataFrame) -> Pipeline:
    """
    Trains a polynomial model based on the variables specified in the YML file, if the YML file
    has the field ["training"]["type"] = "polyfit".

    Args:
        configFile (str): The path to the YML file.
        allDfList (List[pd.DataFrame]): A list of Pandas dataframes.

    Returns:
        Pipeline: The trained polynomial model.
    """
    # Read the YML file
    yml_data = readYMLfile(configFile)

    # Check if the type of training is polynomial fitting
    if yml_data['training']['type'] == 'PolyFeat':
        # Get the variables to be used in the training
        var_list = yml_data['training']['variables']
        interaction_only = yml_data['training']['interaction_only']
        
        # Create the pipeline
        pipe = Pipeline([('PolyFeat', PolynomialFeatures(degree=3, include_bias=True, interaction_only=interaction_only)), 
                         ('LinearReg', LinearRegression())])
        
        # Prepare the data for the training
       
        Xfinal = dfTotal[var_list]
        yfinal = dfTotal['realWeight']
        
        # Fit the model
        pipe.fit(Xfinal, yfinal)
        
        # Return the trained model
        return pipe, Xfinal, yfinal
    else:
        raise ValueError("Invalid training type specified in YML file.")


def testWooby(pipe, XTest, yTest, name=""):
    """
    This function evaluates the performance of a given pipeline model on the test dataset.

    Args:
        pipe (Pipeline): A trained pipeline model.
        XTest (DataFrame): The test dataset features.
        yTest (Series): The test dataset target variable.

    Returns:
        DataFrame: A dataframe with the model evaluation metrics.
    """
    yPredict = pipe.predict(XTest)

    allDataTest = XTest.copy()
    allDataTest["realWeight"] = yTest
    allDataTest["predictWeight"] = yPredict
    allDataTest["absError"] = allDataTest["predictWeight"] - allDataTest["realWeight"]
    allDataTest["relativeError"] = allDataTest["absError"] / allDataTest["realWeight"]

    dfKPI = pd.DataFrame({
        "name": name,
        "MAE": [np.abs(allDataTest["absError"]).mean()],
        "RMSE": [np.sqrt(((allDataTest["absError"])**2).mean())],
        "R": [pipe.score(XTest, yTest)],
        "MaxAE": [np.abs(allDataTest["absError"]).max()]
    })

    return allDataTest, dfKPI


def train_and_test_wooby(modelFolder:str, configFile:str):
    """
    This function trains and tests a Wooby model using the given configuration file and model folder.

    Args:
        modelFolder (str): The path to the model folder.
        configFile (str): The path to the configuration file.

    Returns:
        tuple: A tuple with two elements. The first element is a DataFrame with the test data and predictions. The second element is a DataFrame with the performance metrics.
    """
    

    fileNameList = listFilesForTraining(configFile)

    allDfList = importCSVbatch(fileNameList, "")

    add_real_weight_to_dataframes(fileNameList, allDfList)

    # Creation of the test DataFrame
    dfTotal = pd.concat(allDfList, ignore_index=True)

    # Training 
    modelPolyFeat, XTrainPolyFeat, YTrainPolyFeat = trainWooby(configFile, dfTotal) 
    allDataTest, dfKPI = testWooby(modelPolyFeat, XTrainPolyFeat, YTrainPolyFeat, name = extract_model_name(configFile))

    return modelPolyFeat, dfKPI, allDataTest


##############################        
#   Genetics AI functions    #
##############################


def generate_weight_function(df_x, df_y, pop_size=100, num_gen=100, mutation_rate=0.05):
    """
    Generates a mathematical function to calculate the real weight based on the variables 'relativeVal_WU1',
    'relativeVal_WU2', and 'relativeVal_WU3' using a genetic algorithm.

    Args:
        df_x (pandas.DataFrame): A pandas DataFrame containing the variables 'relativeVal_WU1', 'relativeVal_WU2', and
            'relativeVal_WU3'.
        df_y (pandas.DataFrame): A pandas DataFrame containing the real weight of the run.
        pop_size (int): The size of the population for the genetic algorithm.
        num_gen (int): The number of generations for the genetic algorithm.
        mutation_rate (float): The mutation rate for the genetic algorithm.

    Returns:
        callable: A callable function that takes as input a list of values for the variables 'relativeVal_WU1',
            'relativeVal_WU2', and 'relativeVal_WU3' and returns an estimate of the real weight.

    """
    # Define the variables and parameters for the genetic algorithm
    num_params = 3
    param_range = [-10, 10]
    population = [[random.uniform(param_range[0], param_range[1]) for _ in range(num_params)] for _ in range(pop_size)]

    # Define the fitness function for the genetic algorithm
    def fitness_func(individual):
        y_pred = np.dot(df_x, individual)
        return mean_squared_error(df_y, y_pred)

    # Run the genetic algorithm
    for i in range(num_gen):
        fitness_scores = [fitness_func(individual) for individual in population]
        sorted_indices = np.argsort(fitness_scores)
        sorted_population = [population[i] for i in sorted_indices]
        elites = sorted_population[:int(pop_size * 0.1)]
        new_population = elites.copy()
        while len(new_population) < pop_size:
            parent1 = random.choice(sorted_population)
            parent2 = random.choice(sorted_population)
            child = []
            for j in range(num_params):
                if random.random() < mutation_rate:
                    child.append(random.uniform(param_range[0], param_range[1]))
                else:
                    if random.random() < 0.5:
                        child.append(parent1[j])
                    else:
                        child.append(parent2[j])
            new_population.append(child)
        population = new_population

    # Define the final fitness function to optimize
    def final_fitness_func(individual):
        y_pred = np.dot(df_x, individual)
        return mean_squared_error(df_y, y_pred)

    # Use the SciPy minimize function to find the best individual
    result = minimize(final_fitness_func, population[0], method='BFGS')
    best_individual = result.x

    # Define the weight function using the best individual
    weight_func = lambda x: np.dot(x, best_individual)

    return weight_func




def add_real_weight_to_dataframes(fileNameList: List[str], allDfList: List[pd.DataFrame]) -> List[pd.DataFrame]:
    """
    Given a list of file names and a list of dataframes, this function extracts the weight from the file name
    and adds it as a column "realWeight" to the corresponding dataframe.

    Args:
        fileNameList (list of str): A list of file names.
        allDfList (list of pd.DataFrame): A list of dataframes.

    Returns:
        list of pd.DataFrame: The list of dataframes with the "realWeight" column added.
    """
    for ii, file in enumerate(fileNameList):
        mtch = re.search(r"(\d*)gr", file)
        allDfList[ii]["realWeight"] = float(mtch.group(1))
        
    return allDfList









def convert_df(df):
    """
    Converts a DataFrame with columns for measurements of 3 different sensors and metadata into a new DataFrame 
    with columns for each individual measurement and a "sensor" column to indicate which sensor the measurement 
    corresponds to.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        The DataFrame to be converted. Must contain the following columns: 
        'realWeight', 'relValWU1_mean', 'relValWU1_std', 'relValWU2_mean', 'relValWU2_std', 'relValWU3_mean',
        'relValWU3_std', 'relValWU1_norm_mean', 'relValWU1_norm_std', 'relValWU2_norm_mean', 'relValWU2_norm_std', 
        'relValWU3_norm_mean', 'relValWU3_norm_std', 'test'.
        
    Returns:
    --------
    pandas.DataFrame
        The converted DataFrame with columns 'sensor', 'realWeight', 'mean', 'std', 'norm_mean', 'norm_std'.
    """
   
    final_df = pd.DataFrame()
    
    # Create a dictionary to map column names to sensor values
    col_to_sensor = {'relValWU1': 1, 'relValWU2': 2, 'relValWU3': 3}
    
    # Loop through each measurement type and add columns to new_df
    for col_prefix in col_to_sensor.keys():
        
        # Extract the realWeight and test columns
        new_df = df[['realWeight', 'test']].copy()
        
        col_mean = col_prefix + '_mean'
        col_std = col_prefix + '_std'
        col_norm_mean = col_prefix + '_norm_mean'
        col_norm_std = col_prefix + '_norm_std'
        sensor_num = col_to_sensor[col_prefix]
        
        # Add columns for mean, std, norm_mean, and norm_std
        new_df['mean'] = df[col_mean]
        new_df['std'] = df[col_std]
        new_df['norm_mean'] = df[col_norm_mean]
        new_df['norm_std'] = df[col_norm_std]
        
        # Add column for sensor number
        new_df['sensor'] = sensor_num
        
        
        if final_df.empty:
            final_df = new_df
        else:
            final_df = pd.concat([final_df, new_df], ignore_index=True) 
        print("")
        print("")
        
        print(final_df)
    
    # Reorder the columns in the new DataFrame
    new_df = new_df[['sensor', 'realWeight', 'mean', 'std', 'norm_mean', 'norm_std']]
    
    return final_df


def plot_test(df, xVar, yVar , ax=None, color_=None):
    # Set the plotting style
    sns.set_style("whitegrid")
    
    # Create the plot
    if ax == None:
        fig, ax = plt.subplots(figsize=(10, 6))
    
    
    # Plot each model's predicted mean value vs real weight
    if color_ == None:
        ax.scatter(df[xVar], df[yVar], alpha=0.5, label=df["test"].loc[0])
    else:
        ax.scatter(df[xVar], df[yVar], alpha=0.5, label=df["test"].loc[0], color=color_)
        
    
    # Add a legend and axis labels
    ax.legend()
    ax.set_xlabel("Real weight (gr)")
    ax.set_ylabel("Abslolute value (gr)")
    
    # Show the plot
    plt.show()
    
    return ax
    


def sanityCheck(df: pd.DataFrame) -> pd.DataFrame:
    result_df = df.groupby("realWeight").agg(
        relValWU1_mean=pd.NamedAgg(column="relativeVal_WU1", aggfunc="mean"),
        relValWU1_std=pd.NamedAgg(column="relativeVal_WU1", aggfunc="std"),
        relValWU2_mean=pd.NamedAgg(column="relativeVal_WU2", aggfunc="mean"),
        relValWU2_std=pd.NamedAgg(column="relativeVal_WU2", aggfunc="std"),
        relValWU3_mean=pd.NamedAgg(column="relativeVal_WU3", aggfunc="mean"),
        relValWU3_std=pd.NamedAgg(column="relativeVal_WU3", aggfunc="std"),
    )

    result_df["relValWU1_norm_mean"] = np.where(result_df.index == 0, np.nan, result_df["relValWU1_mean"] / result_df.index)
    result_df["relValWU1_norm_std"] = np.where(result_df.index == 0, np.nan, result_df["relValWU1_std"] / result_df.index)
    result_df["relValWU2_norm_mean"] = np.where(result_df.index == 0, np.nan, result_df["relValWU2_mean"] / result_df.index)
    result_df["relValWU2_norm_std"] = np.where(result_df.index == 0, np.nan, result_df["relValWU2_std"] / result_df.index)
    result_df["relValWU3_norm_mean"] = np.where(result_df.index == 0, np.nan, result_df["relValWU3_mean"] / result_df.index)
    result_df["relValWU3_norm_std"] = np.where(result_df.index == 0, np.nan, result_df["relValWU3_std"] / result_df.index)

    result_df = result_df.reset_index()
    return result_df


