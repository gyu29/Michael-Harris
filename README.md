# DAX Pattern Trading System

A Python-based algorithmic trading system that identifies specific price patterns in financial markets, generates trading signals, and performs backtesting to evaluate strategy performance.

## Overview

This system analyzes price data to identify specific candlestick patterns across multiple timeframes. It generates buy and sell signals based on predefined conditions, and then performs backtesting with configurable stop-loss and take-profit percentages to evaluate the strategy's performance.

## Features

- Pattern recognition algorithm that identifies specific high/low price relationships
- Signal generation for buy (2), sell (1), or no signal (0)
- Backtesting with optimizable parameters
- Performance visualization with candlestick charts and signal indicators
- Comprehensive backtest results summary

## Project Structure

```
Michael-Harris/
├── config.py                  # Configuration parameters
├── dax_trading_pattern/src       # Core package
    ├── data_loader.py            # Backtesting implementation
    └── init.py
├── main.py                    # Main execution script
├── notebooks/                 # Jupyter notebook originally inspired from
├── preprocessing_data/        
│   └── signal_generator.py    # Signal generation logic
├── requirements.txt           # Dependencies
└── trading_signals/
    ├── backtest.py            # Backtesting implementation
    ├── utils.py               # Utility functions
    └── visualization.py       # Charting and visualization
```

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

The system uses the following default parameters (configurable in `config.py`):

- Stop-loss: 4% of position value
- Take-profit: 2% of position value
- Position size: 0.1 (10% of available capital)

## Usage

Run the main script with optional arguments:

```bash
python main.py --data_folder ./data_forex --visualize --start_index 300 --num_rows 355
```

Arguments:
- `--data_folder`: Path to folder containing price data CSV files
- `--visualize`: Enable visualization of signals on charts
- `--start_index`: Start index for visualization
- `--num_rows`: Number of rows to visualize

## Trading Strategy

The system identifies patterns based on specific price relationships:

- **Buy Signal (2)**: Generated when a series of high/low relationships across multiple candles matches the buy pattern
- **Sell Signal (1)**: Generated when a series of high/low relationships across multiple candles matches the sell pattern
- **No Signal (0)**: When neither buy nor sell conditions are met

The strategy uses configurable stop-loss and take-profit percentages to manage risk.

## Dependencies

- pandas (2.0.3)
- pandas-ta (0.3.14b0)
- numpy (1.24.3)
- plotly (5.15.0)
- tqdm (4.65.0)
- backtesting (0.3.3)

## Backtest Results

The system provides comprehensive backtest results including:
- Aggregated returns
- Number of trades
- Maximum drawdown
- Win rate
- Best/worst/average trade performance
