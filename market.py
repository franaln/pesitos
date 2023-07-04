import os

import pandas as pd
import yfinance as yf

from utils import *

# Cedears names and ratios
df_cedears = pd.read_csv('cedears.csv', sep=',', names=['ticker_us', 'name', '_', 'ticker_ar', 'ratio'])
df_cedears['ticker_ar'] = df_cedears['ticker_ar'].str.strip()
df_cedears['ticker_us'] = df_cedears['ticker_us'].str.strip()

date_now = pd.to_datetime("now")
str_today = date_now.strftime(date_fmt)
str_lastd = (date_now - pd.Timedelta(days=1)).strftime(date_fmt)
str_lastw = (date_now - pd.Timedelta(days=7)).strftime(date_fmt)

# Some utils
def get_db_path(ticker):
    ticker_str = ticker.replace('.', '_')
    return f'db/prices_{ticker_str}.csv'

def is_old(path):
    diff = pd.to_datetime("now") - pd.Timestamp(os.path.getmtime(path), unit='s')
    return diff > pd.Timedelta(minutes=30)

def get_yesterday_str(date):
    if isinstance(date, str):
        date = pd.to_datetime(date)
    return (date - pd.Timedelta(days=1)).strftime(date_fmt)

def fix_price_data(df):
    df.loc[:,'Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    #df = df.resample('1D').ffill()
    #df = df[['Adj Close']]
    #df = df.rename(columns={'Adj Close': 'price'})
    return df

def load_price_data(path):
    df = pd.read_csv(path)
    return fix_price_data(df)

def save_price_data(data, path):
    data = data.drop_duplicates()
    data.to_csv(path)

def get_last_valid_date(date):
    if isinstance(date, str):
        date = pd.to_datetime(date)

    if date.day_of_week == 5:
        date = date - pd.Timedelta(days=1)
    elif date.day_of_week == 6:
        date = date - pd.Timedelta(days=2)
    
    return date.strftime(date_fmt)

#
def get_price_now(ticker):
    
    ticker_str = ticker.replace('.', '_')
    path =  f'db/current_price_{ticker_str}.csv'

    if not os.path.exists(path) or is_old(path):
        try:
            data = yf.download(ticker_str, period='1d', progress=False)
            save_price_data(data, path)
        except:
            print(f'Error downloading current price for {ticker}. Using last value or 0')

    if os.path.exists(path):
        data = load_price_data(path)
        
        try:
            price = data['Adj Close'][0]
        except:
            price = None
    else:
        price = None # FIX?
        
    if price is None:
        print('No current price, using the last value', str_lastd)
        price = get_price(ticker, str_lastd)

    return price


def get_price(ticker, date):
    
    path = get_db_path(ticker)

    date = get_last_valid_date(date)

    if os.path.exists(path):
        data = load_price_data(path)
        if date not in data.index:

            try:
                last_date = data.index[-1].strftime(date_fmt)
            except IndexError:
                last_date = str_lastw

            new_data = yf.download(ticker, start=last_date, end=str_today, interval='1d')
            data = pd.concat([data, new_data]).drop_duplicates()
            save_price_data(data, path)
            print(new_data)

    else:
        data = yf.download(ticker, start=str_lastw, end=str_today, interval='1d')
        save_price_data(data, path)
        
    try:
        price = data.loc[date, 'Adj Close']
    except:
        print(f'Problem getting price for {ticker} and {date}, so setting to 0')
        if debug:
            print(data)
        price = 0

    if debug:
        print('Price', ticker, date, path, price)

    return price


def get_price_yesterday(ticker, date=None):
    if date is None:
        return get_price(ticker, str_lastd)
    else:
        return get_price(ticker, get_yesterday_str(date))

def get_price_cedear(ticker, date=None):

    """
    Return price at date if not None or the last price otherwise
    """

    info = df_cedears[df_cedears['ticker_ar']==ticker]
    info.reset_index(inplace=True)

    if info.empty:
        return {}
    
    ticker_ar = f'{ticker}.BA'
    ticker_us = info['ticker_us'][0].strip()

    try:
        ratio = float(info['ratio'][0])
    except:
        ratio = 1

    if date is not None:
        price_ar = get_price(ticker_ar, date)
        price_us = get_price(ticker_us, date)

        price_ar_1d = get_price_yesterday(ticker_ar, date)
        price_us_1d = get_price_yesterday(ticker_us, date)

    else:
        price_ar = get_price_now(ticker_ar)
        price_us = get_price_now(ticker_us)

        price_ar_1d = get_price_yesterday(ticker_ar)
        price_us_1d = get_price_yesterday(ticker_us)

    price_ar_change_1d = (price_ar - price_ar_1d) / price_ar_1d if price_ar_1d > 0 else 0
    price_us_change_1d = (price_us - price_us_1d) / price_us_1d if price_us_1d > 0 else 0

    try:
        ccl = (ratio * price_ar) / price_us
    except ZeroDivisionError:
        ccl = 0

    return {
        'price_ar':           price_ar,
        'price_us':           price_us,
        'price_ar_change_1d': price_ar_change_1d,
        'price_us_change_1d': price_us_change_1d,
        'ccl':                ccl
    }


def get_price_arstock(ticker, date=None):

    """
    Return price at date if not None or the last price otherwise
    """

    ticker_ar = f'{ticker}.BA'

    if date is not None:
        price_ar = get_price(ticker_ar, date)
        price_ar_1d = get_price_yesterday(ticker_ar, date)
    else:
        price_ar = get_price_now(ticker_ar)
        price_ar_1d = get_price_yesterday(ticker_ar)

    price_ar_change_1d = (price_ar - price_ar_1d) / price_ar_1d if price_ar_1d > 0 else 0

    return {
        'price_ar':           price_ar,
        'price_ar_change_1d': price_ar_change_1d,
        'price_us':           0,
        'price_us_change_1d': 0,
        'ccl':                0,
        }


def get_prices_at_date(tickers, date=None):

    rows = []
    for ticker, kind in tickers:
        print(ticker)

        if kind == 'AR':
            d = get_price_arstock(ticker, date)
        elif kind == 'CAR':
            d = get_price_cedear(ticker, date)
        
        d['ticker'] = ticker

        rows.append(d)

        cols=[
            'ticker', 
            'price_ar', 
            'price_us', 
            'price_ar_change_1d', 
            'price_us_change_1d',
            'ccl',
            ]

    return pd.DataFrame(rows, columns=cols)
