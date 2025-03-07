# data_downloader.py

import pandas as pd
import requests

ticker = 'eurusd'
start_date = '20031201'
end_date = '20250307'
interval = 'd'

url = f'https://stooq.com/q/d/l/?s={ticker}&d1={start_date}&d2={end_date}&i={interval}'

response = requests.get(url)

with open(f'{ticker}_historical_data.csv', 'wb') as file:
    file.write(response.content)

print(f'Historical data for {ticker.upper()} saved to {ticker}_historical_data.csv')
