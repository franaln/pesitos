import datetime

import numpy as np
import pandas as pd

from market import get_prices_at_date


date_fmt = '%Y-%m-%d'

class Portfolio:

    def __init__(self):


        self.db = None
        self.load_txs()

        self.tickers = list(set([ (t, k) for t, k in self.df_txs[['ticker', 'kind']].values if k!='BONO']))

        self.start_date = self.df_txs.index[0]
        self.today  = pd.to_datetime("now")
        self.end_date   = (self.today - pd.Timedelta(days=1))

        self.last_market_update = None


    def load_txs(self):

        df_bm  = pd.read_csv('txs_bm.txt',  names=['date', 'ticker', 'kind', 'op', 'n', 'price', 'total'])
        df_ieb = pd.read_csv('txs_ieb.txt', names=['date', 'ticker', 'kind', 'op', 'n', 'price', 'total'])

        df_bm ['broker'] = 'BM'
        df_ieb['broker'] = 'IEB'

        self.df_txs = pd.concat([df_bm, df_ieb])

        self.df_txs.date = pd.to_datetime(self.df_txs.date, format='%Y-%m-%d')
        self.df_txs.set_index('date', inplace=True)
        self.df_txs.sort_index(inplace=True)


    def get_portfolio_at_date(self, date=None):

        if date is None:
            date_pd = pd.to_datetime(self.today, format='%Y-%m-%d')
        else:
            date_pd = pd.to_datetime(date, format='%Y-%m-%d')

        rows = []

        df_tmp = self.df_txs.loc[:date]

        for ticker, dfg in df_tmp.groupby('ticker'):

            # effective price (including fees):  total / n
            dfg['peff'] = dfg['total'] / dfg['n']

            # effective n (removing sells and gains/losses from those sells)
            dfg['neff'] = np.where(dfg['op'] != 'Venta', dfg['n'], 0).astype('int')

            for sidx, srow in dfg.iterrows():
                if srow['op'] != 'Venta':
                    continue

                # for each cell remove the stocks starting from the beginning
                sn = abs(int(srow['n']))

                # loop from the beggining
                for bidx, brow in dfg.iterrows():

                    # skip sells or buys with neff=0 or idxs after sell
                    if brow['op'] == 'Venta' or brow['neff'] == 0:
                        continue

                    if bidx >= sidx:
                        break

                    if brow['neff'] <= sn:
                        dfg.loc[bidx,'neff'] = 0
                        sn -= brow['neff']
                    else:
                        dfg.loc[bidx,'neff'] = brow['neff'] - sn
                        sn = 0

                    if sn == 0:
                        break

            # effective total
            dfg['teff'] = np.where(dfg['op'] != 'Venta', dfg['neff'] * dfg['peff'], 0)

            total_n  = dfg['neff'].sum()
            total_p  = dfg['teff'].sum()

            if total_n == 0:
                continue

            ppc = total_p / total_n

            dfg['days'] = (date_pd - dfg.index).days

            dfg['weight'] = dfg['neff'] / total_n
            dfg['days_w'] = dfg['days'] * dfg['weight']

            days_avg = dfg['days_w'].sum()

            # tpc = date_pd - pd.Timedelta(days=days_avg)

            rows.append([ticker, total_n, ppc, int(days_avg), total_p])

        cols = ['ticker', 'n', 'ppc', 'days_avg', 'total_ar']

        return pd.DataFrame(rows,columns=cols)



    def load(self):
        self.db = self.get_portfolio_at_date()

    def update_market(self):
        now = datetime.datetime.now()
        if self.last_market_update is None or (now - self.last_market_update).seconds > 1800:
            self.df_market = get_prices_at_date(self.tickers, None)
            print(self.df_market)
            self.last_market_update = now


    def update(self):

        #print('Portfolio: ')
        #print(self.db)

        self.update_market()
        #print('Market:')
        #print(self.df_market)

        self.dbm = pd.merge(self.db, self.df_market)

        self.dbm.loc[:,'total_ar_now'] = self.dbm['n'] * self.dbm['price_ar']

        # returns
        self.dbm.loc[:,'diff_unit'] = self.dbm['price_ar'] - self.dbm['ppc']
        self.dbm.loc[:,'diff'] = self.dbm['total_ar_now'] - self.dbm['total_ar']
        self.dbm.loc[:,'diff_pp'] = self.dbm['diff'] / self.dbm['total_ar']
        self.dbm.loc[:,'diff_pp_1mo'] = 30 * self.dbm['diff_pp'] / self.dbm['days_avg']


        # Total and fractions
        total_ar = self.dbm['total_ar'].sum()
        total_ar_now = self.dbm['total_ar_now'].sum()
        total_diff = self.dbm['diff'].sum()

        self.dbm.loc[:,'fraction'] = self.dbm['total_ar_now'] / total_ar_now
        
        #print(self.dbm)

        self.total_dict = {
            'ticker': 'Total',
            'n': None,
            'ppc': None,
            'days_avg': None,
            'total_ar': total_ar,
            'price_ar': None,
            'price_us': None,
            'total_ar_now': total_ar_now,
            'diff': total_diff,
            'diff_unit': None,
            'diff_pp': total_diff / total_ar,
            'diff_pp_1mo': None,
            'fraction': 1,
            #'ccl': None,
        }

