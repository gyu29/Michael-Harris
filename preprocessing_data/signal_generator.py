import pandas as pd
import numpy as np
from tqdm import tqdm

def total_signal(df, current_candle):
    current_pos = df.index.get_loc(current_candle)
    
    if current_pos < 3:
        return 0
    
    c1 = df['High'].iloc[current_pos] > df['High'].iloc[current_pos-1]
    c2 = df['Low'].iloc[current_pos] > df['High'].iloc[current_pos-2]
    c3 = df['Low'].iloc[current_pos-1] > df['High'].iloc[current_pos-3]
    
    if c1 and c2 and c3:
        return 2
    
    c1 = df['Low'].iloc[current_pos] < df['Low'].iloc[current_pos-1]
    c2 = df['High'].iloc[current_pos] < df['Low'].iloc[current_pos-2]
    c3 = df['High'].iloc[current_pos-1] < df['Low'].iloc[current_pos-3]
    
    if c1 and c2 and c3:
        return 1

    return 0

def original_total_signal(df, current_candle):
    current_pos = df.index.get_loc(current_candle)
    
    if current_pos < 3:
        return 0
    
    c1 = df['High'].iloc[current_pos] > df['High'].iloc[current_pos-1]
    c2 = df['High'].iloc[current_pos-1] > df['Low'].iloc[current_pos]
    c3 = df['Low'].iloc[current_pos] > df['High'].iloc[current_pos-2]
    c4 = df['High'].iloc[current_pos-2] > df['Low'].iloc[current_pos-1]
    c5 = df['Low'].iloc[current_pos-1] > df['High'].iloc[current_pos-3]
    c6 = df['High'].iloc[current_pos-3] > df['Low'].iloc[current_pos-2]
    c7 = df['Low'].iloc[current_pos-2] > df['Low'].iloc[current_pos-3]

    if c1 and c2 and c3 and c4 and c5 and c6 and c7:
        return 2
    
    c1 = df['Low'].iloc[current_pos] < df['Low'].iloc[current_pos-1]
    c2 = df['Low'].iloc[current_pos-1] < df['High'].iloc[current_pos]
    c3 = df['High'].iloc[current_pos] < df['Low'].iloc[current_pos-2]
    c4 = df['Low'].iloc[current_pos-2] < df['High'].iloc[current_pos-1]
    c5 = df['High'].iloc[current_pos-1] < df['Low'].iloc[current_pos-3]
    c6 = df['Low'].iloc[current_pos-3] < df['High'].iloc[current_pos-2]
    c7 = df['High'].iloc[current_pos-2] < df['High'].iloc[current_pos-3]

    if c1 and c2 and c3 and c4 and c5 and c6 and c7:
        return 1

    return 0

def add_total_signal(df, use_simplified=True):
    if use_simplified:
        df['TotalSignal'] = df.progress_apply(lambda row: total_signal(df, row.name), axis=1)
    else:
        df['TotalSignal'] = df.progress_apply(lambda row: original_total_signal(df, row.name), axis=1)
    return df

def add_pointpos_column(df, signal_column):
    def pointpos(row):
        if row[signal_column] == 2:
            return row['Low'] - 1e-4
        elif row[signal_column] == 1:
            return row['High'] + 1e-4
        else:
            return np.nan

    df['pointpos'] = df.apply(lambda row: pointpos(row), axis=1)
    return df

def multi_timeframe_signal(df):
    df_1h = df.resample('1H').agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last'})
    df_4h = df.resample('4H').agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last'})
    
    df_1h = add_total_signal(df_1h)
    df_4h = add_total_signal(df_4h)
    
    df['Signal_1h'] = np.nan
    df['Signal_4h'] = np.nan
    
    for idx in df.index:
        df.loc[idx, 'Signal_1h'] = df_1h.loc[idx:idx, 'TotalSignal'].iloc[0] if idx in df_1h.index else 0
        df.loc[idx, 'Signal_4h'] = df_4h.loc[idx:idx, 'TotalSignal'].iloc[0] if idx in df_4h.index else 0
    
    df['CombinedSignal'] = 0
    df.loc[(df['TotalSignal'] == 2) & (df['Signal_1h'] == 2), 'CombinedSignal'] = 2
    df.loc[(df['TotalSignal'] == 1) & (df['Signal_1h'] == 1), 'CombinedSignal'] = 1
    
    return df