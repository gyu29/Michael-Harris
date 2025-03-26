# Pattern configuration settings

DEFAULT_PATTERN_CONFIG = {
    'use_simplified': False,
    'pattern_length': 3,
    'min_price_change': 0.001,  # 0.1% minimum price change
    'max_price_change': 0.05,   # 5% maximum price change
    'volume_threshold': 1.2,    # 20% above average volume
    'timeframe': '1D'           # Default timeframe
}

SIMPLIFIED_PATTERN_CONFIG = {
    'use_simplified': True,
    'pattern_length': 2,
    'min_price_change': 0.002,  # 0.2% minimum price change
    'max_price_change': 0.03,   # 3% maximum price change
    'volume_threshold': 1.1,    # 10% above average volume
    'timeframe': '1D'           # Default timeframe
} 