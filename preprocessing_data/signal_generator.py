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

def multi_timeframe_signal(df, current_candle, timeframes=[5, 15, 30]):
    current_pos = df.index.get_loc(current_candle)
    if current_pos < max(timeframes) + 3:
        return 0
    
    signals = []
    base_signal = total_signal(df, current_candle)
    signals.append(base_signal)
    
    for tf in timeframes:
        subset_length = current_pos + 1
        subset = df.iloc[max(0, current_pos - subset_length * 2):current_pos + 1]
        
        resampled = subset.resample(f'{tf}T').agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last'
        }).dropna()
        
        if len(resampled) > 3:
            tf_signal = total_signal(resampled, resampled.index[-1])
            signals.append(tf_signal)
    
    buy_signals = signals.count(2)
    sell_signals = signals.count(1)
    
    if buy_signals > sell_signals and buy_signals > len(signals) / 3:
        return 2
    elif sell_signals > buy_signals and sell_signals > len(signals) / 3:
        return 1
    else:
        return 0