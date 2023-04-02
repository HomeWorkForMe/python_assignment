import requests
import argparse
from model import FinancialData, db, args
from sqlalchemy.dialects.sqlite import insert
from requests.exceptions import ConnectionError
import os
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path('env/.env'))


# Load from .env file
API_KEY = os.getenv("API_KEY")


def get_data(symbol, get_full_data=False):
    if get_full_data:
        url = f'https://www.alphavantage.co/query?' \
              f'function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&outputsize=full&apikey={API_KEY}'
    else:
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&apikey={API_KEY}'
    try:
        r = requests.get(url)
        if r.status_code != 200:
            print('[ERROR!!] Cannot get data this time, please try again later.')
            return
    except ConnectionError:
        print('[ERROR!!] Cannot connect to the internet, please check your connection.')
        return

    data = r.json()
    daily = data["Time Series (Daily)"]
    rows = []
    dates = list(daily.keys())

    # Skip weekends, 2 weeks ago is the latest 10 weekdays
    if not get_full_data:
        dates = dates[: 10]
    for date in dates:
        row = dict()
        info = daily[date]

        # Handle data of wrong format by skipping
        if not all(key in info for key in {'1. open', '4. close', '6. volume'}):
            print(f'Got data in wrong format, skipped data of symbol {symbol}, date {date}')

        row['date'] = date
        row['symbol'] = symbol
        row['open_price'] = info['1. open']
        row['close_price'] = info['4. close']
        row['volume'] = info['6. volume']
        rows.append(row)
    db.session.execute(statement=upsert_stmt(), params=rows)
    db.session.commit()
    print(f'Finishing download and process data for symbol {symbol}')


def upsert_stmt():
    stmt = insert(FinancialData)
    return stmt.on_conflict_do_update(
        index_elements=['date', 'symbol'],
        set_={
            'open_price': stmt.excluded.open_price,
            'close_price': stmt.excluded.close_price,
            'volume': stmt.excluded.volume,
        })


if __name__ == "__main__":
    full_data = args.get_full_data
    get_data('AAPL', get_full_data=full_data)
    get_data('IBM', get_full_data=full_data)
