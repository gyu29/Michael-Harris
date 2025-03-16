import pandas as pd
import requests

ticker = '^spx'
start_date = '20151201'
end_date = '20250316'
interval = 'd'

url = f'https://stooq.com/q/d/l/?s={ticker}&d1={start_date}&d2={end_date}&i={interval}'

response = requests.get(url)

with open(f'spx_historical_data.csv', 'wb') as file:
    file.write(response.content)

print(f'Historical data for S&P 500 saved to spx_historical_data.csv')