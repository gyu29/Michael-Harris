import pandas as pd
from tqdm import tqdm
import argparse
from dax_pattern_trading.src.data_loader import read_data_folder
from preprocessing_data.signal_generator import generate_signals, add_pointpos_column, multi_timeframe_signal
from preprocessing_data.pattern_config import DEFAULT_PATTERN_CONFIG, SIMPLIFIED_PATTERN_CONFIG
from trading_signals.backtest import run_backtest, run_backtest_with_cv
from trading_signals.visualization import plot_candlestick_with_signals, plot_backtest_results
import numpy as np

def main():
    parser = argparse.ArgumentParser(description='DAX Pattern Trading System')
    parser.add_argument('--data_folder', type=str, default='./dax_pattern_trading/data', 
                    help='Path to the folder containing price data CSV files')
    parser.add_argument('--visualize', action='store_true', 
                        help='Visualize signals on charts')
    parser.add_argument('--start_index', type=int, default=300,
                        help='Start index for visualization')
    parser.add_argument('--num_rows', type=int, default=355,
                        help='Number of rows to visualize')
    parser.add_argument('--use_simplified', action='store_true',
                        help='Use simplified pattern recognition')
    parser.add_argument('--cross_validation', action='store_true',
                        help='Use cross-validation for backtesting')
    parser.add_argument('--multi_timeframe', action='store_true',
                        help='Use multi-timeframe signal confirmation')
    args = parser.parse_args()
    
    print("Loading data from", args.data_folder)
    dataframes, file_names = read_data_folder(args.data_folder)
    
    print("Generating trading signals...")
    for i, df in enumerate(dataframes):
        print("Working on dataframe", i, "...")
        
        pattern_config = SIMPLIFIED_PATTERN_CONFIG if args.use_simplified else DEFAULT_PATTERN_CONFIG
        df = generate_signals(df, pattern_config)
        
        if args.multi_timeframe and df.index.dtype.kind == 'M':
            try:
                df = multi_timeframe_signal(df)
                signal_column = 'CombinedSignal'
            except Exception as e:
                print(f"Could not apply multi-timeframe analysis: {e}")
                signal_column = 'TotalSignal'
        else:
            signal_column = 'TotalSignal'
            
        df = add_pointpos_column(df, signal_column)
        dataframes[i] = df 
    
    signal_counts = sum([frame["TotalSignal"].value_counts() for frame in dataframes], start=0)
    print("\nSignal distribution:")
    print(f"No signal: {signal_counts.get(0, 0)}")
    print(f"Sell signals: {signal_counts.get(1, 0)}")
    print(f"Buy signals: {signal_counts.get(2, 0)}")
    
    if args.visualize and len(dataframes) > 0:
        print("\nVisualizing signals...")
        plot_candlestick_with_signals(dataframes[0], args.start_index, args.num_rows)
    
    print("\nRunning backtests...")
    if args.cross_validation:
        results, stats, heatmaps = run_backtest_with_cv(dataframes)
    else:
        results, heatmaps = run_backtest(dataframes)
    
    agg_returns = sum([r["Return [%]"] for r in results])
    num_trades = sum([r["# Trades"] for r in results])
    max_drawdown = min([r["Max. Drawdown [%]"] for r in results])
    
    if results:
        avg_drawdown = sum([r["Avg. Drawdown [%]"] for r in results]) / len(results)
        win_rate = sum([r["Win Rate [%]"] for r in results]) / len(results)
        best_trade = max([r["Best Trade [%]"] for r in results])
        worst_trade = min([r["Worst Trade [%]"] for r in results])
        avg_trade = sum([r["Avg. Trade [%]"] for r in results]) / len(results)
        
        try:
            sharpe = sum([r["Sharpe Ratio"] for r in results]) / len(results)
            sortino = sum([r["Sortino Ratio"] for r in results]) / len(results)
            calmar = sum([r["Calmar Ratio"] for r in results]) / len(results)
        except KeyError:
            sharpe = sortino = calmar = 0.0
            
        print("\nBacktest Results Summary:")
        print(f"Aggregated Returns: {agg_returns:.2f}%")
        print(f"Number of Trades: {num_trades}")
        print(f"Maximum Drawdown: {max_drawdown:.2f}%")
        print(f"Average Drawdown: {avg_drawdown:.2f}%")
        print(f"Win Rate: {win_rate:.2f}%")
        print(f"Best Trade: {best_trade:.2f}%")
        print(f"Worst Trade: {worst_trade:.2f}%")
        print(f"Average Trade: {avg_trade:.2f}%")
        print(f"Sharpe Ratio: {sharpe:.2f}")
        print(f"Sortino Ratio: {sortino:.2f}")
        print(f"Calmar Ratio: {calmar:.2f}")
        
        plot_backtest_results(results)
    else:
        print("No backtest results to display")

if __name__ == "__main__":
    tqdm.pandas()
    main()