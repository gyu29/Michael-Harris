import pandas as pd
import pandas_ta as ta
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from backtesting import Strategy, Backtest
import time

def fetch_data(symbol, start_date, end_date):
    stock = yf.Ticker(symbol)
    df = stock.history(start=start_date, end=end_date)
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

    # Symmetrical conditions for short (sell condition)
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
    signals = []
    for i in range(len(df)):
        if i < 3:
            signals.append(0)
        else:
            signals.append(total_signal(df, df.index[i]))
    
    df['TotalSignal'] = signals
    return df

def SIGNAL(df):
    return df.TotalSignal

class MyStrategy(Strategy):
    mysize = 0.1  # Trade size
    slperc = 0.04  # Stop loss percentage
    tpperc = 0.02  # Take profit percentage

    def init(self):
        super().init()
        self.signal1 = self.I(SIGNAL, self.data)

    def next(self):
        super().next()
        
        if self.signal1 == 2 and not self.position:
            # Open a new long position with calculated SL and TP
            current_close = self.data.Close[-1]
            sl = current_close - self.slperc * current_close  # SL at 4% below the close price
            tp = current_close + self.tpperc * current_close  # TP at 2% above the close price
            self.buy(size=self.mysize, sl=sl, tp=tp)

        elif self.signal1 == 1 and not self.position:
            current_close = self.data.Close[-1]
            sl = current_close + self.slperc * current_close  # SL at 4% above the close price
            tp = current_close - self.tpperc * current_close  # TP at 2% below the close price
            self.sell(size=self.mysize, sl=sl, tp=tp)

def run_backtest(symbol, start_date, end_date):
    print(f"\nRunning backtest for {symbol} from {start_date} to {end_date}")
    
    df = fetch_data(symbol, start_date, end_date)
    df = add_total_signal(df)
    bt = Backtest(df, MyStrategy, cash=10000, margin=1/5, commission=0.0002)
    start_time = time.time()
    stats = bt.optimize(
        slperc=[i/100 for i in range(1, 8)],
        tpperc=[i/100 for i in range(1, 8)],
        maximize='Return [%]',
        max_tries=100,
        random_state=0
    )
    end_time = time.time()
    print("\n" + "="*50)
    print(f"BACKTEST RESULTS FOR {symbol}")
    print("="*50)
    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
    duration_days = (end_date_obj - start_date_obj).days
    
    print(f"Start Time: {start_date}")
    print(f"End Time: {end_date}")
    print(f"Duration: {duration_days} days")
    print(f"Exposure Time [%]: {stats['Exposure Time [%]']:.2f}%")
    print(f"Equity Final [$]: ${stats['Equity Final [$]']:.2f}")
    print(f"Equity Peak [$]: ${stats['Equity Peak [$]']:.2f}")
    print(f"Return [%]: {stats['Return [%]']:.2f}%")
    print(f"Buy & Hold Return [%]: {stats['Buy & Hold Return [%]']:.2f}%")
    print(f"Return (Ann.) [%]: {stats['Return (Ann.) [%]']:.2f}%")
    print(f"Volatility (Ann.) [%]: {stats['Volatility (Ann.) [%]']:.2f}%")
    print(f"Sharpe Ratio: {stats['Sharpe Ratio']:.2f}")
    print(f"Sortino Ratio: {stats['Sortino Ratio']:.2f}")
    print(f"Calmar Ratio: {stats['Calmar Ratio']:.2f}")
    print(f"Max Drawdown [%]: {stats['Max. Drawdown [%]']:.2f}%")
    print(f"Avg Drawdown [%]: {stats['Avg. Drawdown [%]']:.2f}%")
    print(f"Max Drawdown Duration: {stats['Max. Drawdown Duration']}")
    print(f"Avg. Drawdown Duration: {stats['Avg. Drawdown Duration']}")
    print(f"# Trades: {stats['# Trades']}")
    print(f"Win Rate [%]: {stats['Win Rate [%]']:.2f}%")
    print(f"Best Trade [%]: {stats['Best Trade [%]']")
