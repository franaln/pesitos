import os
from functools import reduce

import pandas as pd
import yfinance as yf

#from pandas.tseries.holiday import USFederalHolidayCalendar as us_holidays
#holidays = us_holidays()

import utils


date_now = pd.to_datetime("now")
str_today = date_now.strftime(utils.date_fmt)
str_lastd = (date_now - pd.Timedelta(days=1)).strftime(utils.date_fmt)
str_lastw = (date_now - pd.Timedelta(days=7)).strftime(utils.date_fmt)

# Some utils

class Market:

    def __init__(self, tickers):

        self.tickers = tickers


        self.db_now = None
        self.db_old = None


        self.last_update = None



    def get_db_path(ticker):
        ticker_str = ticker.replace('.', '_')
        return f'db/prices_{ticker_str}.csv'

    def is_old(self, path):
        diff = pd.to_datetime("now") - pd.Timestamp(os.path.getmtime(path), unit='s')
        return diff > pd.Timedelta(minutes=30)

    def download_data(self, ticker, start, end):
        data = yf.download(ticker, start=start, end=end,
                           progress=False, interval='1d')
        if not data.empty:
            data.loc[:,'status'] = 'downloaded'
        return data

    def get_last_valid_date(self, date):

        date = get_date(date)

        # 5/6 are Saturday and Sunday so return Friday
        if date.day_of_week == 5:
            date = date - pd.Timedelta(days=1)
        elif date.day_of_week == 6:
            date = date - pd.Timedelta(days=2)

        # Not considering holidays

        return get_date_str(date)

    def load_price_data(self, path):
        data = pd.read_csv(path)
        #data.drop_duplicates(subset='Date', inplace=True)
        data.loc[:,'Date'] = pd.to_datetime(data['Date'], format='%Y-%m-%d')
        data.set_index('Date', inplace=True)
        #df = df.resample('1D').ffill()
        #df = df[['Adj Close']]
        #df = df.rename(columns={'Adj Close': 'price'})

        # if not data.empty and 'status' not in data.columns:
        #     data.loc[:,'status'] = 'downloaded'

        return data

    def save_price_data(self, data, path):
        data = data.reset_index()
        data.loc[:,'Date'] = data['Date'].dt.strftime('%Y-%m-%d')
        data.to_csv(path, index=False)

    def update_data(self, path, ticker, date):
        str_p3 = utils.get_date_prev(date, 3)
        str_n3 = utils.get_date_next(date, 3)

        data = self.download_data(ticker, str_p3, str_n3)

        # add to current data if exists
        if os.path.exists(path):
            old_data = self.load_price_data(path)
            data = pd.concat([old_data, data])
            data = data.reset_index().drop_duplicates(subset='Date', keep='first').set_index('Date')
            data.sort_index(inplace=True)

        self.save_price_data(data, path)


    def get_price_stock_ar(self, ticker_dict, date, include_change):

        """
        Return price at date if not None or the last price otherwise
        """

        if date == 'now':
            price_ar = self.get_price_now(ticker_dict['ticker_ar'])
        else:
            price_ar = self.get_price(ticker_dict['ticker_ar'], date)

        if include_change:
            price_ar_1d = self.get_price_prev(ticker_dict['ticker_ar'], date)

            if price_ar_1d is not None and price_ar_1d > 0:
                price_ar_change_1d = (price_ar - price_ar_1d) / price_ar_1d
            else:
                price_ar_change_1d = 0
        else:
            price_ar_change_1d = 0

        return {
            'price_ar':           price_ar,
            'price_ar_change_1d': price_ar_change_1d,
        }


    def get_price_stock_car(self, ticker_dict, date, include_change):

        """
        Return price at date if not None or the last price otherwise
        """

        if date == 'now':
            price_ar = self.get_price_now(ticker_dict['ticker_ar'])
            price_us = self.get_price_now(ticker_dict['ticker_us'])
        else:
            price_ar = self.get_price(ticker_dict['ticker_ar'], date)
            price_us = self.get_price(ticker_dict['ticker_us'], date)

        if include_change:
            price_ar_1d = self.get_price_prev(ticker_dict['ticker_ar'], date)
            price_us_1d = self.get_price_prev(ticker_dict['ticker_us'], date)

            if price_ar_1d is not None and price_ar_1d > 0:
                price_ar_change_1d = (price_ar - price_ar_1d) / price_ar_1d
            else:
                price_ar_change_1d = 0

            if price_us_1d is not None and price_us_1d > 0:
                price_us_change_1d = (price_us - price_us_1d) / price_us_1d
            else:
                price_us_change_1d = 0

        else:
            price_ar_change_1d = 0
            price_us_change_1d = 0


        if price_us is not None and price_ar is not None and price_us > 0:
            ccl = (ticker_dict['ratio'] * price_ar) / price_us
        else:
            ccl = None

        return {
            'price_ar':           price_ar,
            'price_us':           price_us,
            'price_ar_change_1d': price_ar_change_1d,
            'price_us_change_1d': price_us_change_1d,
            'ccl': ccl,
        }



    def get_price_prev(self, ticker, date):

        if date == 'now':
            date = str_today

        date_prev = utils.get_date_prev(date, 1)

        ticker_str = ticker.replace('.', '_')
        path = f'db/prices_{ticker_str}.csv'
        #path = get_db_path(ticker)
        data = self.load_price_data(path)

        price = None
        if date_prev in data.index:
            price = data.loc[date_prev, 'Adj Close']
        else:
            for i in range(1, 10):
                date_prev = utils.get_date_prev(date_prev, i)
                if date_prev in data.index:
                    price = data.loc[date_prev, 'Adj Close']
                    break

        if price is not None:
            data.loc[date] = data.loc[date_prev]
            data.loc[date, 'status'] = 'prev'
            data = data.reset_index().drop_duplicates(subset='Date', keep='first')
            data.loc[:,'Date'] = pd.to_datetime(data['Date'], format='%Y-%m-%d')
            data.set_index('Date', inplace=True)
            data.sort_index(inplace=True)
            self.save_price_data(data, path)

        return price


    def get_price(self, ticker, date):

        ticker_str = ticker.replace('.', '_')
        path = f'db/prices_{ticker_str}.csv'

        #date = get_last_valid_date(date)

        if not os.path.exists(path):
            # str_p3 = get_date_prev(date, 3)
            # str_n3 = get_date_next(date, 3)
            # print(f'Downloading data for {ticker} from {str_p3} to {str_n3}')
            # data = download_data(ticker, str_p3, str_n3)
            # save_price_data(data, path)
            self.update_data(path, ticker, date)

        #
        data = self.load_price_data(path)

        if date not in data.index:
            self.update_data(path, ticker, date)
            data = self.load_price_data(path)

        try:
            price = data.loc[date, 'Adj Close']
        except:
            print(f'Problem getting price for {ticker} and {date} -> using previous value')
            price = self.get_price_prev(ticker, date)
            # save this prev value as {date} to avoid next problem (but if this only a tmp problem??)

        return price


    def get_price_now(self, ticker):

        ticker_str = ticker.replace('.', '_')
        path =  f'db/current_price_{ticker_str}.csv'

        if not os.path.exists(path) or self.is_old(path):
            try:
                data = yf.download(ticker, period='1d', progress=False)
                self.save_price_data(data, path)
            except:
                print(f'Error downloading current price for {ticker}. Using last value or 0')

        if os.path.exists(path):
            data = self.load_price_data(path)

            try:
                price = data['Adj Close'][0]
            except:
                price = None
        else:
            price = None # FIX?

        if price is None:
            print('No current price, using the last value', str_lastd)
            price = self.get_price(ticker, str_lastd)

        return price


    def get_now_ccl(self):
        # Compute current CCL average value
        return self.db_now['ccl'].mean(skipna=True)

    def get_now_db(self):
        return self.db_now

    def get_db(self):
        return self.db_old

    def get_db_on_date(self, date):
        return self.db_old.xs(date, level=0)

    def get_ccl_on_date(self, date):
        return self.db_old.xs(date, level=0)['ccl'].mean()

    def get_ccl_db(self):
        return self.db_old.groupby('date')[['ccl']].mean()

    def load_old_prices_db(self, dates, include_change=False, add_ccl=False):

        print(f'[Market] loading old prices  ...')

        rows = []
        for date in dates:

            for ticker in self.tickers:

                if ticker['kind'] == 'AR':
                    d = self.get_price_stock_ar(ticker, date, include_change)
                elif ticker['kind'] == 'CAR':
                    d = self.get_price_stock_car(ticker, date, include_change)


                d['date'] = date
                d['ticker'] = ticker['ticker']

                rows.append(d)

        cols = [
            'date',
            'ticker',
            'price_ar',
            'price_us',
            'ccl',
        ]
        if include_change:
            cols.extend([
                'price_ar_change_1d',
                'price_us_change_1d',
            ])


        self.db_old = pd.DataFrame(rows, columns=cols)
        self.db_old.set_index(['date', 'ticker'], inplace=True)

        # if add_ccl:
        #     df_ccl = pd.DataFrame(rows_ccl, columns=['date', 'ccl'])
        #     df_ccl.set_index('date', inplace=True)
        #     return df, df_ccl
        # else:
        # return df

    def update_now_db(self):

        print(f'[Market] updating ... ')

        rows = []
        for ticker in self.tickers:

            if ticker['kind'] == 'AR':
                d = self.get_price_stock_ar(ticker, 'now', include_change=True)
            elif ticker['kind'] == 'CAR':
                d = self.get_price_stock_car(ticker, 'now', include_change=True)

            d['ticker'] = ticker['ticker']

            rows.append(d)

        cols = [
            'ticker',
            'price_ar',
            'price_us',
            'price_ar_change_1d',
            'price_us_change_1d',
            'ccl',
        ]

        self.db_now = pd.DataFrame(rows, columns=cols)
        self.last_update = pd.to_datetime('now')



# ## ----------------------------
# ## ----------------------------

# def is_old(path):
#     diff = pd.to_datetime("now") - pd.Timestamp(os.path.getmtime(path), unit='s')
#     return diff > pd.Timedelta(minutes=30)

# def download_data(ticker, start, end):
#     data = yf.download(ticker, start=start, end=end,
#                        progress=False, interval='1d')

#     if not data.empty:
#         data.loc[:,'status'] = 'downloaded'

#     return data


def load_price_data(path):
    data = pd.read_csv(path)
    #data.drop_duplicates(subset='Date', inplace=True)
    data.loc[:,'Date'] = pd.to_datetime(data['Date'], format='%Y-%m-%d')
    data.set_index('Date', inplace=True)
    #df = df.resample('1D').ffill()
    #df = df[['Adj Close']]
    #df = df.rename(columns={'Adj Close': 'price'})

    # if not data.empty and 'status' not in data.columns:
    #     data.loc[:,'status'] = 'downloaded'

    return data

# def save_price_data(data, path):
#     data = data.reset_index()
#     data.loc[:,'Date'] = data['Date'].dt.strftime('%Y-%m-%d')
#     data.to_csv(path, index=False)

# def update_data(path, ticker, date):
#     str_p3 = utils.get_date_prev(date, 3)
#     str_n3 = utils.get_date_next(date, 3)

#     data = download_data(ticker, str_p3, str_n3)

#     # add to current data if exists
#     if os.path.exists(path):
#         old_data = load_price_data(path)
#         data = pd.concat([old_data, data])
#         data = data.reset_index().drop_duplicates(subset='Date', keep='first').set_index('Date')
#         data.sort_index(inplace=True)

#     save_price_data(data, path)

# ## ----------------------------
# ## ----------------------------


# def get_last_valid_date(date):

#     date = get_date(date)

#     # 5/6 are Saturday and Sunday so return Friday
#     if date.day_of_week == 5:
#         date = date - pd.Timedelta(days=1)
#     elif date.day_of_week == 6:
#         date = date - pd.Timedelta(days=2)

#     # Not considering holidays

#     return get_date_str(date)

# #
# def get_price_now(ticker):

#     ticker_str = ticker.replace('.', '_')
#     path =  f'db/current_price_{ticker_str}.csv'

#     if not os.path.exists(path) or is_old(path):
#         try:
#             data = yf.download(ticker, period='1d', progress=False)
#             save_price_data(data, path)
#         except:
#             print(f'Error downloading current price for {ticker}. Using last value or 0')

#     if os.path.exists(path):
#         data = load_price_data(path)

#         try:
#             price = data['Adj Close'][0]
#         except:
#             price = None
#     else:
#         price = None # FIX?

#     if price is None:
#         print('No current price, using the last value', str_lastd)
#         price = get_price(ticker, str_lastd)

#     return price


# def get_price(ticker, date):

#     ticker_str = ticker.replace('.', '_')
#     path = f'db/prices_{ticker_str}.csv'

#     #date = get_last_valid_date(date)

#     if not os.path.exists(path):
#         # str_p3 = get_date_prev(date, 3)
#         # str_n3 = get_date_next(date, 3)
#         # print(f'Downloading data for {ticker} from {str_p3} to {str_n3}')
#         # data = download_data(ticker, str_p3, str_n3)
#         # save_price_data(data, path)

#         update_data(path, ticker, date)


#     #
#     data = load_price_data(path)

#     if date not in data.index:
#         update_data(path, ticker, date)
#         data = load_price_data(path)

#     try:
#         price = data.loc[date, 'Adj Close']
#     except:
#         print(f'Problem getting price for {ticker} and {date} -> using previous value')
#         price = get_price_prev(ticker, date)
#         # save this prev value as {date} to avoid next problem (but if this only a tmp problem??)

#     return price


# def get_price_prev(ticker, date):

#     if date == 'now':
#         date = str_today

#     date_prev = utils.get_date_prev(date, 1)

#     ticker_str = ticker.replace('.', '_')
#     path = f'db/prices_{ticker_str}.csv'
#     #path = get_db_path(ticker)
#     data = load_price_data(path)

#     price = None
#     if date_prev in data.index:
#         price = data.loc[date_prev, 'Adj Close']
#     else:
#         for i in range(1, 10):
#             date_prev = utils.get_date_prev(date_prev, i)
#             if date_prev in data.index:
#                 price = data.loc[date_prev, 'Adj Close']
#                 break

#     if price is not None:
#         data.loc[date] = data.loc[date_prev]
#         data.loc[date, 'status'] = 'prev'
#         data = data.reset_index().drop_duplicates(subset='Date', keep='first')
#         data.loc[:,'Date'] = pd.to_datetime(data['Date'], format='%Y-%m-%d')
#         data.set_index('Date', inplace=True)
#         data.sort_index(inplace=True)
#         save_price_data(data, path)

#     return price


# def get_price_stock_car(ticker_ar, ticker_us, date, include_change):

#     """
#     Return price at date if not None or the last price otherwise
#     """

#     #print_debug(f'[get_price_stock_car] {ticker_ar=}, {ticker_us=}, {date=}')

#     if date == 'now':
#         price_ar = get_price_now(ticker_ar)
#         price_us = get_price_now(ticker_us)
#     else:
#         price_ar = get_price(ticker_ar, date)
#         price_us = get_price(ticker_us, date)

#     if include_change:
#         price_ar_1d = get_price_prev(ticker_ar, date)
#         price_us_1d = get_price_prev(ticker_us, date)

#         if price_ar_1d is not None and price_ar_1d > 0:
#             price_ar_change_1d = (price_ar - price_ar_1d) / price_ar_1d
#         else:
#             price_ar_change_1d = 0

#         if price_us_1d is not None and price_us_1d > 0:
#             price_us_change_1d = (price_us - price_us_1d) / price_us_1d
#         else:
#             price_us_change_1d = 0

#     else:
#         price_ar_change_1d = 0
#         price_us_change_1d = 0

#     return {
#         'price_ar':           price_ar,
#         'price_us':           price_us,
#         'price_ar_change_1d': price_ar_change_1d,
#         'price_us_change_1d': price_us_change_1d,
#     }


# def get_price_stock_ar(ticker_ar, date, include_change):

#     """
#     Return price at date if not None or the last price otherwise
#     """

#     #print(f'[Market] {ticker_ar=}, {date=}')

#     if date == 'now':
#         price_ar = get_price_now(ticker_ar)
#     else:
#         price_ar = get_price(ticker_ar, date)

#     if include_change:
#         price_ar_1d = get_price_prev(ticker_ar, date)

#         if price_ar_1d is not None and price_ar_1d > 0:
#             price_ar_change_1d = (price_ar - price_ar_1d) / price_ar_1d
#         else:
#             price_ar_change_1d = 0
#     else:
#         price_ar_change_1d = 0

#     return {
#         'price_ar':           price_ar,
#         'price_us':           None,
#         'price_ar_change_1d': price_ar_change_1d,
#         'price_us_change_1d': None,
#         }




# def get_prices_df(tickers, dates, include_change=False, add_ccl=False):

#     print(f'[Market] get prices dataframe  ...')

#     rows = []
#     rows_ccl = []
#     for date in dates:

#         ccl_avg, ccl_count = 0, 0
#         for ticker in tickers:

#             if ticker['kind'] == 'AR':
#                 d = get_price_stock_ar(ticker['ticker_ar'], date, include_change)
#             elif ticker['kind'] == 'CAR':
#                 d = get_price_stock_car(ticker['ticker_ar'], ticker['ticker_us'], date, include_change)

#                 try:
#                     ccl_avg += (ticker['ratio'] * d['price_ar']) / d['price_us']
#                     ccl_count += 1
#                 except:
#                     pass

#             d['date'] = date
#             d['ticker'] = ticker['ticker']

#             rows.append(d)


#         # Compute avergage CCL for each date
#         ccl_avg /= ccl_count
#         rows_ccl.append({'date': date, 'ccl': ccl_avg})


#     cols = [
#         'date',
#         'ticker',
#         'price_ar',
#         'price_us',
#     ]
#     if include_change:
#         cols.extend([
#             'price_ar_change_1d',
#             'price_us_change_1d',
#         ])


#     df = pd.DataFrame(rows, columns=cols)
#     df.set_index(['date', 'ticker'], inplace=True)

#     if add_ccl:
#         df_ccl = pd.DataFrame(rows_ccl, columns=['date', 'ccl'])
#         df_ccl.set_index('date', inplace=True)
#         return df, df_ccl
#     else:
#         return df


# def get_prices_now_df(tickers):

#     print(f'[Market] get prices now dataframe  ...')

#     rows = []
#     # rows_ccl = []
#     ccl_avg, ccl_count = 0, 0
#     for ticker in tickers:

#         if ticker['kind'] == 'AR':
#             d = get_price_stock_ar(ticker['ticker_ar'], 'now', include_change=True)
#         elif ticker['kind'] == 'CAR':
#             d = get_price_stock_car(ticker['ticker_ar'], ticker['ticker_us'], 'now', include_change=True)

#             ccl_avg += (ticker['ratio'] * d['price_ar']) / d['price_us']
#             ccl_count += 1

#         #d['date'] = 'now' ##date
#         d['ticker'] = ticker['ticker']

#         rows.append(d)

#     # Compute avergage CCL for each date
#     ccl_avg /= ccl_count

#     cols = [
#         'date',
#         'ticker',
#         'price_ar',
#         'price_us',
#         'price_ar_change_1d',
#         'price_us_change_1d',
#     ]

#     df = pd.DataFrame(rows, columns=cols)
#     ##df.set_index(['date', 'ticker'], inplace=True)

#     return df, ccl_avg


def get_prices_df(tickers):

    dfs = []
    for ticker in tickers:

        df = load_price_data(get_db_path(ticker))

        df[ticker] = df[['Adj Close']]

        dfs.append(df[ticker])

    df_merged = reduce(lambda  left,right: pd.merge(left, right, on=['Date'], how='outer'), dfs)

    return df_merged
