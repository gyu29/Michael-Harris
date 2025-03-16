# data_loader.py

import pandas as pd
import pandas_ta as ta
from tqdm import tqdm
import os
import numpy as np

def read_csv_to_dataframe(file_path):
    df = pd.read_csv(file_path)
    date_column = "Gmt time" if "Gmt time" in df.columns else "Date"
    
    if date_column == "Gmt time":
        df[date_column] = df[date_column].str.replace(".000", "")
        df[date_column] = pd.to_datetime(df[date_column], format='%d.%m.%Y %H:%M:%S')
    else:
        df[date_column] = pd.to_datetime(df[date_column])
    df = df[df.High != df.Low]
    df.set_index(date_column, inplace=True)
    
    return df

def read_data_folder(folder_path="./data"):
    dataframes = []
    file_names = []
    for file_name in tqdm(os.listdir(folder_path)):
        if file_name.endswith('.csv'):
            file_path = os.path.join(folder_path, file_name)
            df = read_csv_to_dataframe(file_path)
            dataframes.append(df)
            file_names.append(file_name)
    return dataframes, file_names
