import os
import datetime

import numpy as np
import pandas as pd

import utils
from market import Market

class Portfolio:

    def __init__(self):

        # self.db = None
        self.load_txs()

        self.tickers_dict = utils.tickers_dict
        self.tickers_list = utils.tickers_list

        self.tickers = [ ticker['ticker'] for ticker in self.tickers_list ]


        # self.start_date = pd.to_datetime('2022-01-01') ##self.db_txs.index[0]
        self.today = pd.to_datetime("now")
        self.end_date   = (self.today - pd.Timedelta(days=1))

        start_date_str = '2021-05-18' #get_date_str(self.start_date)
        mid_date_str   = '2023-07-15'
        last_date_str  = utils.get_date_str(self.end_date)

        # Prices
        dates = pd.date_range(start_date_str, last_date_str, freq='d').strftime(utils.date_fmt).to_list()

        self.market = Market(self.tickers_list)
        self.market.load_old_prices_db(dates)

        print('[Portfolio] loading prices ...')

        self.db_prices = self.market.get_db() ##market.get_prices_df(self.tickers_list, dates, include_change=False, add_ccl=True)
        self.db_ccl = self.market.get_ccl_db()

        #
        self.dates = pd.date_range(start_date_str, mid_date_str, freq='m').strftime(utils.date_fmt).to_list()
        self.dates += pd.date_range(mid_date_str, last_date_str, freq='d').strftime(utils.date_fmt).to_list()

        #
        print('[Portfolio] loading past porfolios ...')
        pfs = []
        for date in self.dates:

            ccl_est = self.db_ccl.loc[date,'ccl']

            # load or recompute pf
            if not os.path.exists(f'db/pf_{date}.csv'):
                pf = self.get_portfolio_at_date(date, self.db_ccl)
                pf.to_csv(f'db/pf_{date}.csv', index=False)


            # Read from file and expand
            pf = pd.read_csv(f'db/pf_{date}.csv')
            ## add date to use as index
            pf.loc[:,'date'] = date

            #print(pf)
            #print(db_prices.xs(date, level=0))

            prices_date = self.db_prices.xs(date, level=0).reset_index()

            ## expand: FIX, esta mal lo de USD
            pfe = self.expand_portfolio(pf, prices_date, ccl_est)

            pfs.append(pfe)


        self.pfs = pd.concat(pfs)
        self.pfs.set_index(['date', 'ticker'], inplace=True)


        # Current portfolio
        print('[Portfolio] loading current porfolio ...')
        # if not os.path.exists('db/pf_now.csv'):
        #     pf.to_csv('db/pf_now.csv', index=False)
        # self.cpf = pd.read_csv(f'db/pf_now.csv')

        self.last_market_update = None
        self.update_current_portfolio()

        print('[Portfolio] initialization done.')



    def load_txs(self):

        print('[Portfolio] loading txs ...')

        cols = ['date', 'ticker', 'kind', 'op', 'n', 'price', 'total']

        dfs = []
        for broker in ('bm', 'ieb'):
            df = pd.read_csv('txs_bm.txt',  names=cols, comment='#')
            df['broker'] = broker
            dfs.append(df)

        self.db_txs = pd.concat(dfs)

        self.db_txs.date = pd.to_datetime(self.db_txs.date, format='%Y-%m-%d')
        self.db_txs.set_index('date', inplace=True)
        self.db_txs.sort_index(inplace=True)


    def get_portfolio_at_date(self, date, db_ccl=None):

        # FIX: this can be improved not computing everything for each date

        print(f'[Portfolio] creating portfolio for date = {date}') ## using CCL={ccl_avg:.2f}')

        if date == 'now':
            date_pd = utils.get_date(self.today)
            df_tmp = self.db_txs
        else:
            date_pd = utils.get_date(date)
            df_tmp = self.db_txs.loc[:date]




        rows = []

        for ticker, dfg in df_tmp.groupby('ticker'):

            if ticker not in self.tickers:
                continue

            print(dfg)
            print(db_ccl)

            # effective price (including fees):  total / n
            dfg['peff'] = dfg['total'] / dfg['n']

            # estimate price in usd using average ccl
            dfg['peff_usd'] = dfg.apply(lambda x: x['peff'] / db_ccl.loc[x.name.strftime(utils.date_fmt), 'ccl'], axis=1)

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

            # in usd
            dfg['teff_usd'] = np.where(dfg['op'] != 'Venta', dfg['neff'] * dfg['peff_usd'], 0)

            total_n  = dfg['neff'].sum()
            total_p  = dfg['teff'].sum()
            total_usd  = dfg['teff_usd'].sum()

            if total_n == 0:
                continue

            ppc = total_p / total_n

            # buy weights
            dfg['weight'] = dfg['neff'] / total_n

            # estimate average time of buys using buy weights
            dfg['days']   = (date_pd - dfg.index).days
            dfg['days_w'] = dfg['days'] * dfg['weight']
            days_avg = int(dfg['days_w'].sum())

            # estimate averate date of buy
            tpc = utils.get_date_str(date_pd - pd.Timedelta(days=days_avg))

            rows.append([ticker, total_n, ppc, tpc, total_p, total_usd])

        cols = ['ticker', 'n', 'ppc', 'tpc', 'total', 'total_usd']

        return pd.DataFrame(rows, columns=cols)


    # def load(self, date):
    #     self.db = self.get_portfolio_at_date(date)

    # def update_market(self):
    #     #self.df_market = get_prices_at_date(self.tickers, '2023-07-05', include_change=True)
    #     if self.last_market_update is None or (now - self.last_market_update).seconds > 1800:
    #         self.df_market = get_prices_at_date(self.tickers, 'now')
    #         self.last_market_update = now
    #         self.date = now.strftime('%Y-%m-%d %H:%M')

    def update_current_portfolio(self):
        now = datetime.datetime.now()
        # if self.last_market_update is None or (now - self.last_market_update).seconds > 1800:
        print('[Portfolio] updating current portfolio ...')

        self.market.update_now_db()
        db_prices = self.market.get_now_db()

        cpf = self.get_portfolio_at_date('now', self.db_ccl)

        self.cpf = self.expand_portfolio(cpf, db_prices, self.market.get_now_ccl())

        #self.date = last_date_str
        self.last_market_update = now
        self.date = now.strftime('%Y-%m-%d %H:%M')
        print('[Portfolio] updating current portfolio ... done')

    def expand_portfolio(self, pf, prices, ccl):

        ## add prices
        pfe = pd.merge(pf, prices)

        # totals
        ##pfe.loc[:,'total']     = pfe['n'] * pfe['ppc']

        print(pfe.head())

        pfe.loc[:,'total_now']     = pfe['n'] * pfe['price_ar']
        pfe.loc[:,'total_now_usd'] = pfe['total_now'] / ccl

        # returns
        # pfe.loc[:,'diff_unit']   = pfe['price_ar'] - pfe['ppc']
        pfe.loc[:,'diff'] = pfe['total_now'] - pfe['total']
        pfe.loc[:,'diff_pct'] = pfe['diff'] / pfe['total']

        pfe.loc[:,'diff_usd'] = pfe['total_now_usd'] - pfe['total_usd']
        pfe.loc[:,'diff_pct_usd'] = pfe['diff_usd'] / pfe['total_usd']


        pfe.loc[:,'days'] = (self.today - pd.to_datetime(pfe['tpc'], format=utils.date_fmt))
        pfe.loc[:,'days'] = pfe['days'].dt.days

        # dayly/weekly/monthly returns
        pfe.loc[:,'diff_pct_1d'] =  pfe['diff_pct'] / pfe['days']
        pfe.loc[:,'diff_pct_1w'] =   7 * pfe['diff_pct_1d']
        pfe.loc[:,'diff_pct_1m'] =  30 * pfe['diff_pct_1d']
        pfe.loc[:,'diff_pct_1y'] = 365 * pfe['diff_pct_1d']

        pfe.loc[:,'diff_pct_1d_usd'] =  pfe['diff_pct_usd'] / pfe['days']
        pfe.loc[:,'diff_pct_1w_usd'] =   7 * pfe['diff_pct_1d_usd']
        pfe.loc[:,'diff_pct_1m_usd'] =  30 * pfe['diff_pct_1d_usd']
        pfe.loc[:,'diff_pct_1y_usd'] = 365 * pfe['diff_pct_1d_usd']

        # cedears

        ## add tmp columns: kind and ratio
        pfe.loc[:,'kind']  = pfe['ticker'].map({ ticker: td['kind'] for ticker, td in self.tickers_dict.items() })
        pfe.loc[:,'ratio'] = pfe['ticker'].map({ ticker: td['ratio'] for ticker, td in self.tickers_dict.items() })

        pfe.loc[:,'ccl'] = np.where(pfe['kind']=='CAR', (pfe['ratio'] * pfe['price_ar']) / pfe['price_us'], None)
        pfe.loc[:,'n_us'] = np.where(pfe['kind']=='CAR', pfe['n']/pfe['ratio'], None)

        # Total and fractions
        pfe.loc[:,'fraction'] = pfe['total_now'] / pfe['total_now'].sum()

        return pfe


    def get_date(self):
        return self.date

    def get_data(self):
        return self.cpf

    def get_dict(self):
        return self.cpf.to_dict('records')

    def get_total_dict(self):

        # Totals
        total     = self.cpf['total'].sum()
        total_now = self.cpf['total_now'].sum()
        total_diff   = self.cpf['diff'].sum()

        # Total USD
        total_usd      = self.cpf['total_usd'].sum()
        total_now_usd  = self.cpf['total_now_usd'].sum()
        total_diff_usd = self.cpf['diff_usd'].sum()

        # ccl_avg = db_car['ccl'].sum() / len(db_car)
        # total_us = total_ar / ccl_avg
        # total_us_now = total_ar_now / ccl_avg

        total_dict = {
            'total': total,
            'total_now': total_now,
            'total_usd': total_usd,
            'total_now_usd': total_now_usd,
            'diff': total_diff,
            'diff_pct': total_diff / total,
            'diff_usd': total_diff_usd,
            'diff_pct_usd': total_diff_usd / total_usd,
        }

        return total_dict

    def get_pfs(self):
        return self.pfs

    def get_tickers(self, filter_str=None):

        if filter_str is None:
            return [ ticker for ticker in self.cpf['ticker'] ]
        else:
            dbm_filtered = self.cpf.query(filter_str)
            return [ ticker for ticker in dbm_filtered['ticker'] ]

    def get_weights(self):

        tickers = [ t for t, k in  self.tickers ] ## if k == 'CAR']

        # print(tickers)

        def safe_weight(date, ticker):
            try:
                return self.pfs.xs((date, ticker))['fraction']
            except:
                return 0

        def safe_today_weight(ticker):
            try:
                return self.cpf[self.cpf['ticker']==ticker]['fraction'].to_numpy()[0]
            except:
                return 0

        dates = ('2023-08-01', '2023-07-15', '2023-06-15', '2023-05-15', '2023-04-15', '2023-01-15', '2022-06-01')

        yst = [ [ safe_weight(date, ticker) for ticker in tickers ] for date in dates ]
        today = [ safe_today_weight(ticker) for ticker in tickers ]

        # for ticker in tickers:

        #     for date in ):
        #         try:
        #             yst.append()
        #         except:
        #             yst.append(0)

            # try:
            #     w = self.dbm[self.dbm['ticker']==ticker]['fraction'].to_numpy()[0]
            #     print(ticker, w)
            #     today.append(w)
            # except:
            #     today.append(0)

        #print(self.dbm[self.dbm['ticker']=='AAPL']['fraction'].to_numpy()[0])

        allw = yst+[today,]
        #print(allw)
        curr_w = np.array(allw)
        #print(curr_w)

        return curr_w #.resize((1, curr_w.shape[0]))


    def get_last_pfs(self):
        pass
