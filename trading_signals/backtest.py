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
        self.signal = self.I(lambda: self.data.TotalSignal.astype(int))

    def next(self):
        current_signal = self.signal[-1]
        entry_price = self.data.Close[-1]
        
        if current_signal == 2 and not self.position:  # Buy signal
            sl_price = entry_price * (1 - self.sl_pct)
            risk_per_trade = self.equity * self.position_size
            price_diff = abs(entry_price - sl_price)
            
            if price_diff > 0:
                size = (risk_per_trade / price_diff) // 1
                if size > 0:
                    self.buy(
                        size=size,
                        sl=sl_price,
                        tp=entry_price * (1 + self.tp_pct)
                    )

        elif current_signal == 1 and not self.position:  # Sell signal
            sl_price = entry_price * (1 + self.sl_pct)
            risk_per_trade = self.equity * self.position_size
            price_diff = abs(sl_price - entry_price)
            
            if price_diff > 0:
                size = (risk_per_trade / price_diff) // 1
                if size > 0:
                    self.sell(
                        size=size,
                        sl=sl_price,
                        tp=entry_price * (1 - self.tp_pct)
                    )

def backtest_with_params(df, sl_pct_param, tp_pct_param, position_size_param):
    class ParamPatternStrategy(PatternStrategy):
        sl_pct = sl_pct_param
        tp_pct = tp_pct_param
        position_size = position_size_param

    df = df.copy()
    df['TotalSignal'] = df['TotalSignal'].astype(int)
    
    if df['TotalSignal'].nunique() == 1:
        raise ValueError("No valid trading signals in dataframe")

    print(f"\nSignal distribution in backtest: {df['TotalSignal'].value_counts().to_dict()}")
    print(f"Sample signals: {df['TotalSignal'].head(10).tolist()}")
    print(f"Sample closes: {df['Close'].head(10).round(2).tolist()}")

    bt = Backtest(df, ParamPatternStrategy, 
                 cash=100000,
                 margin=1/5,
                 commission=.002,
                 exclusive_orders=True)
    
    stats = bt.run()
    return process_stats(stats)

def process_stats(stats):
    return {
        "Return [%]": stats['Return [%]'],
        "# Trades": stats['# Trades'],
        "Win Rate [%]": stats.get('Win Rate [%]', float('nan')),
        "Max. Drawdown [%]": stats['Max. Drawdown [%]'],
        "Avg. Drawdown [%]": stats.get('Avg. Drawdown [%]', float('nan')),
        "Best Trade [%]": stats.get('Best Trade [%]', float('nan')),
        "Worst Trade [%]": stats.get('Worst Trade [%]', float('nan')),
        "Avg. Trade [%]": stats.get('Avg. Trade [%]', float('nan')),
        "SQN": stats.get('SQN', float('nan')),
        "Sharpe Ratio": stats.get('Sharpe Ratio', float('nan')),
        "Sortino Ratio": stats.get('Sortino Ratio', float('nan')),
        "Calmar Ratio": stats.get('Calmar Ratio', float('nan')),
    }

def optimize_parameters(df):
    param_grid = {
        'sl_pct': np.arange(0.01, 0.05, 0.005),
        'tp_pct': np.arange(0.01, 0.05, 0.005),
        'position_size': [0.01, 0.02, 0.03]
    }
    
    best_params = None
    best_return = -np.inf
    
    for sl in param_grid['sl_pct']:
        for tp in param_grid['tp_pct']:
            for ps in param_grid['position_size']:
                try:
                    result = backtest_with_params(df, sl, tp, ps)
                    if result['Return [%]'] > best_return and result['# Trades'] > 5:
                        best_return = result['Return [%]']
                        best_params = {'sl': sl, 'tp': tp, 'position_size': ps}
                except Exception as e:
                    print(f"Skipping combination SL:{sl:.3f}, TP:{tp:.3f}, PS:{ps} - {str(e)}")
    
    return best_params

def run_backtest(dataframes):
    results = []
    heatmaps = {}
    
    for i, df in enumerate(tqdm(dataframes, desc="Running backtests")):
        print(f"\nBacktesting dataframe {i} with {len(df)} rows")
        best_params = optimize_parameters(df)
        
        if best_params:
            print(f"Best parameters: {best_params}")
            final_result = backtest_with_params(
                df,
                best_params['sl'],
                best_params['tp'],
                best_params['position_size']
            )
            results.append(final_result)
        else:
            results.append({})
            print("No valid parameters found")
    
    return results, heatmaps

def run_backtest_with_cv(dataframes, n_folds=5):
    """
    Run backtest with cross-validation to provide more robust statistics
    
    Args:
        dataframes: List of pandas DataFrames with trading data
        n_folds: Number of cross-validation folds
        
    Returns:
        results: List of backtest results for each dataframe
        stats: Cross-validation statistics 
        heatmaps: Performance heatmaps (if applicable)
    """
    all_results = []
    all_stats = []
    heatmaps = {}
    
    for i, df in enumerate(tqdm(dataframes, desc="Running CV backtests")):
        print(f"\nBacktesting dataframe {i} with cross-validation")
        if len(df) < n_folds * 10:  # Ensure enough data for CV
            print(f"Not enough data for {n_folds} folds, using single backtest")
            fold_results = [run_backtest([df])[0]]
        else:
            # Split data into folds
            fold_size = len(df) // n_folds
            fold_results = []
            
            for fold in range(n_folds):
                start_idx = fold * fold_size
                end_idx = start_idx + fold_size if fold < n_folds - 1 else len(df)
                test_df = df.iloc[start_idx:end_idx].copy()
                
                print(f"Fold {fold+1}/{n_folds}: Testing on rows {start_idx} to {end_idx}")
                
                # Find optimal parameters on the test fold
                best_params = optimize_parameters(test_df)
                
                if best_params:
                    fold_result = backtest_with_params(
                        test_df,
                        best_params['sl'], 
                        best_params['tp'],
                        best_params['position_size']
                    )
                    fold_results.append(fold_result)
                else:
                    print(f"No valid parameters found for fold {fold+1}")
        
        # Aggregate fold results
        if fold_results:
            # Calculate average statistics across folds
            avg_result = {}
            for key in fold_results[0].keys():
                values = [r.get(key, 0) for r in fold_results if key in r]
                avg_result[key] = sum(values) / len(values) if values else 0
            
            # Calculate standard deviation for confidence intervals
            std_result = {}
            for key in fold_results[0].keys():
                values = [r.get(key, 0) for r in fold_results if key in r]
                std_result[key] = np.std(values) if len(values) > 1 else 0
            
            all_results.append(avg_result)
            all_stats.append({
                'mean': avg_result,
                'std': std_result,
                'fold_results': fold_results
            })
        else:
            all_results.append({})
            all_stats.append({})
            
    return all_results, all_stats, heatmaps
