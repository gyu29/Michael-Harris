import pandas as pd
from tqdm import tqdm
from .pattern_config import DEFAULT_PATTERN_CONFIG, SIMPLIFIED_PATTERN_CONFIG

def generate_signals(df, pattern_config=None):
    if pattern_config is None:
        pattern_config = DEFAULT_PATTERN_CONFIG
        
    df = df.copy()
    
    # Initialize signal column
    df['TotalSignal'] = 0
    
    # Calculate price changes
    df['PriceChange'] = df['Close'].pct_change()
    
    # Calculate volume ratio (current volume / average volume)
    df['VolumeRatio'] = df['Volume'] / df['Volume'].rolling(window=20).mean()
    
    # Pattern detection logic
    for i in range(pattern_config['pattern_length'], len(df)):
        # Get the window of data
        window = df.iloc[i-pattern_config['pattern_length']:i]
        
        # Check if price changes are within bounds
        price_changes = window['PriceChange'].abs()
        if not (price_changes >= pattern_config['min_price_change']).all() or \
           not (price_changes <= pattern_config['max_price_change']).all():
            continue
            
        # Check volume condition
        if window['VolumeRatio'].iloc[-1] < pattern_config['volume_threshold']:
            continue
            
        # Pattern recognition logic
        if pattern_config['use_simplified']:
            # Simplified pattern: Two consecutive candles with opposite directions
            if window['PriceChange'].iloc[-1] > 0 and window['PriceChange'].iloc[-2] < 0:
                df.loc[window.index[-1], 'TotalSignal'] = 2  # Buy signal
            elif window['PriceChange'].iloc[-1] < 0 and window['PriceChange'].iloc[-2] > 0:
                df.loc[window.index[-1], 'TotalSignal'] = 1  # Sell signal
        else:
            # More complex pattern: Three candles with specific relationships
            if window['PriceChange'].iloc[-1] > 0 and \
               window['PriceChange'].iloc[-2] < 0 and \
               window['PriceChange'].iloc[-3] < 0:
                df.loc[window.index[-1], 'TotalSignal'] = 2  # Buy signal
            elif window['PriceChange'].iloc[-1] < 0 and \
                 window['PriceChange'].iloc[-2] > 0 and \
                 window['PriceChange'].iloc[-3] > 0:
                df.loc[window.index[-1], 'TotalSignal'] = 1  # Sell signal
    
    # Convert signals to integer after all calculations
    df['TotalSignal'] = df['TotalSignal'].astype(int)
    
    signal_counts = df['TotalSignal'].value_counts()
    print("\nSignal distribution:")
    print(f"No signal: {signal_counts.get(0, 0)}")
    print(f"Sell signals: {signal_counts.get(1, 0)}")
    print(f"Buy signals: {signal_counts.get(2, 0)}")
    
    return df

def add_pointpos_column(df, signal_column='TotalSignal'):
    df = df.copy()
    df['pointpos'] = None
    
    # Add entry points for visualization
    df.loc[df[signal_column] == 2, 'pointpos'] = df['Low'] * 0.999  # Buy signals
    df.loc[df[signal_column] == 1, 'pointpos'] = df['High'] * 1.001  # Sell signals
    
    return df

def multi_timeframe_signal(df):
    df = df.copy()
    
    # Calculate signals for different timeframes
    df['Signal_1D'] = generate_signals(df, DEFAULT_PATTERN_CONFIG)['TotalSignal']
    df['Signal_4H'] = generate_signals(df.resample('4H').agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum'
    }), DEFAULT_PATTERN_CONFIG)['TotalSignal']
    
    # Combine signals (both timeframes must agree)
    df['CombinedSignal'] = 0
    df.loc[(df['Signal_1D'] == 2) & (df['Signal_4H'] == 2), 'CombinedSignal'] = 2
    df.loc[(df['Signal_1D'] == 1) & (df['Signal_4H'] == 1), 'CombinedSignal'] = 1
    
    return df
