import numpy as np
import pandas as pd
from backtesting import Backtest, Strategy
from tqdm import tqdm
from config import SL_PERCENTAGE, TP_PERCENTAGE, POSITION_SIZE

class PatternStrategy(Strategy):
    sl_pct = SL_PERCENTAGE
    tp_pct = TP_PERCENTAGE
    position_size = POSITION_SIZE
    
    def init(self):
        self.signal = self.data.TotalSignal
        
    def next(self):
        current_signal = self.signal[-1]
        
        if current_signal == 2 and not self.position:
            entry_price = self.data.Close[-1]
            sl_price = entry_price * (1 - self.sl_pct)
            tp_price = entry_price * (1 + self.tp_pct)
            
            self.buy(size=self.position_size * self.equity, sl=sl_price, tp=tp_price)
            
        elif current_signal == 1 and not self.position:
            entry_price = self.data.Close[-1]
            sl_price = entry_price * (1 + self.sl_pct)
            tp_price = entry_price * (1 - self.tp_pct)
            
            self.sell(size=self.position_size * self.equity, sl=sl_price, tp=tp_price)

def backtest_with_params(df, sl_pct_param, tp_pct_param):
    class ParamPatternStrategy(PatternStrategy):
        sl_pct = sl_pct_param
        tp_pct = tp_pct_param
        
    bt = Backtest(df, ParamPatternStrategy, cash=5000, margin=1/5, commission=0.0002)
    stats = bt.run()
    
    result = {
        "Return [%]": stats['Return [%]'],
        "# Trades": stats['# Trades'],
        "Win Rate [%]": stats['Win Rate [%]'],
        "Max. Drawdown [%]": stats['Max. Drawdown [%]'],
        "Avg. Drawdown [%]": stats['Avg. Drawdown [%]'],
        "Best Trade [%]": stats['Best Trade [%]'],
        "Worst Trade [%]": stats['Worst Trade [%]'],
        "Avg. Trade [%]": stats['Avg. Trade [%]'],
        "SQN": stats['SQN'],
        "Sharpe Ratio": stats['Sharpe Ratio'],
        "Sortino Ratio": stats['Sortino Ratio'],
        "Calmar Ratio": stats['Calmar Ratio'],
    }
    
    return result, stats

def optimize_parameters(df):
    train_size = int(len(df) * 0.7)
    train_df = df.iloc[:train_size]
    test_df = df.iloc[train_size:]
    
    best_return = -float('inf')
    best_params = {}
    
    for sl in [0.02, 0.03, 0.04, 0.05]:
        for tp in [0.01, 0.02, 0.03]:
            result, _ = backtest_with_params(train_df, sl, tp)
            
            if result['Return [%]'] > best_return:
                best_return = result['Return [%]']
                best_params = {'sl': sl, 'tp': tp}
    
    test_result, test_stats = backtest_with_params(test_df, best_params['sl'], best_params['tp'])
    
    return best_params, test_result, test_stats

def run_backtest_with_cv(dataframes, num_folds=5):
    all_results = []
    all_stats = []
    heatmaps = []
    
    for df in dataframes:
        fold_size = len(df) // num_folds
        fold_results = []
        fold_stats = []
        
        for i in range(num_folds-1):
            train_df = df.iloc[:fold_size*(i+1)]
            test_df = df.iloc[fold_size*(i+1):fold_size*(i+2)]
            
            result, stats = backtest_with_params(test_df, SL_PERCENTAGE, TP_PERCENTAGE)
            fold_results.append(result)
            fold_stats.append(stats)
            
        all_results.extend(fold_results)
        all_stats.extend(fold_stats)
        
    return all_results, all_stats, heatmaps

def run_backtest(dataframes):
    results = []
    heatmaps = []
    
    for df in dataframes:
        best_params, test_result, test_stats = optimize_parameters(df)
        results.append(test_result)
        
    return results, heatmaps