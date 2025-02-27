import pandas as pd
import pandas_ta as ta
import numpy
import yfinance as yf
from datetime import datetime, timedelta

def fetch_data(symbol, period='1y', interval="1d"):
    stock = yf.Ticker(symbol)
    df = stock.history(period=period, interval=interval)
    df = df[df.High != df.Low]
    return df

def total_signal(df, current_candle):
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

def add_total_signal(df):
    df['TotalSignal'] = df.progress_apply(lambda row: total_signal(df, row.name), axis=1)
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

def analyze_stock(symbol, period="1y", interval="1d"):
    df = fetch_data(symbol, period, interval)
    df = add_total_signal(df)
    df = add_pointpos_column(df, "TotalSignal")
    today = df.index[-1]
    signal = df.loc[today, 'TotalSignal']
    
    if signal == 2:
        print(f"BUY signal for {symbol} on {today.strftime('%Y-%m-%d')}")
    elif signal == 1:
        print(f"SELL signal for {symbol} on {today.strftime('%Y-%m-%d')}")
    else:
        print(f"No signal for {symbol} on {today.strftime('%Y-%m-%d')}")
    
    return df

def main():
    symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"] # stocks to analyze
    
    for symbol in symbols:
        print(f"\nAnalyzing {symbol}...")
        df = analyze_stock(symbol)
        buy_signals = (df['TotalSignal'] == 2).sum()
        sell_signals = (df['TotalSignal'] == 1).sum()
        
        print(f"Total buy signals: {buy_signals}")
        print(f"Total sell signals: {sell_signals}")

if __name__ == "__main__":
    main()