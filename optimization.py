from pypfopt.expected_returns import mean_historical_return, capm_return
from pypfopt.risk_models import CovarianceShrinkage
from pypfopt.efficient_frontier import EfficientFrontier

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from market import get_prices_df



class Optimization:

    def __init__(self, pf):

        self.pf = pf

        self.tickers = [ t for t, k in  pf.tickers ] #if k == 'CAR']

        tickers_ar = [ f'{ticker}.BA' for ticker in self.tickers ]

        # prices
        df_prices = get_prices_df(tickers_ar)
        self.prices = df_prices.rename(columns={ t2: t1 for t1, t2 in zip(self.tickers, tickers_ar)})

        # print(self.prices)


    def optimize(self):

        # returns
        mu_capm = capm_return(self.prices)
        # mu_mean = mean_historical_return(self.prices)

        ## vola
        S = CovarianceShrinkage(self.prices).ledoit_wolf()

        self.ef = EfficientFrontier(mu_capm, S)
        # self.ef2 = EfficientFrontier(mu_mean, S)

        self.ef_opt = self.ef.deepcopy()
        #self.ef2_opt = self.ef.deepcopy()
        self.ef_opt.max_sharpe()
        #self.ef2_opt.max_sharpe()
        #self.opt_weights = self.get_weights()

        self.opt_weights = self.ef_opt.clean_weights()
        #self.ef2_opt_weights = self.ef2_opt.clean_weights()


    def get_current_portfolio_performance(self):
        curr_w = self.pf.get_weights()
        rets = curr_w.dot(self.ef.expected_returns)
        stds = np.sqrt(np.diag(curr_w @ self.ef.cov_matrix @ curr_w.T))
        return rets, stds

    def get_random_portfolios(self, n_samples=100):
        w = np.random.dirichlet(np.ones(self.ef.n_assets), n_samples)
        rets = w.dot(self.ef.expected_returns)
        stds = np.sqrt(np.diag(w @ ef.cov_matrix @ w.T))
        return rets, stds

    def get_optmized_performance(self):
        ret_tangent, std_tangent, _ = self.ef_opt.portfolio_performance()
        return [ret_tangent,], [std_tangent,]

    def get_assets_performance(self):
        return self.ef.expected_returns, np.sqrt(np.diag(self.ef.cov_matrix))


    # Copied from pypfopt.plotting
    def get_efficiency_frontier_contour(self, npoints=100):

        mus, sigmas = [], []

        ef_tmp = self.ef.deepcopy()

        #ef_param_range = _ef_default_returns_range(ef, npoints)

        ef_minvol = ef_tmp.deepcopy()
        ef_maxret = ef_tmp.deepcopy()

        ef_minvol.min_volatility()
        min_ret = ef_minvol.portfolio_performance()[0]
        max_ret = ef_maxret._max_return()
        ef_param_range = np.linspace(min_ret, max_ret - 0.0001, npoints)

        # Create a portfolio for each value of ef_param_range
        for param_value in ef_param_range:
            try:
                ef_tmp.efficient_return(param_value)
            except:
                # warnings.warn(
                print("Could not construct portfolio for parameter value {:.3f}".format(
                        param_value
                    )
                )
                continue

            ret, sigma, _ = ef_tmp.portfolio_performance()
            mus.append(ret)
            sigmas.append(sigma)

        return mus, sigmas


    def get_optmized_with_current_return(self, ret):
        ef_tmp = self.ef.deepcopy()
        ef_tmp.efficient_return(ret)
        ret, sigma, _ = ef_tmp.portfolio_performance()
        return ret, sigma

    def get_optmized_with_current_volatility(self, mus, sigs, vol):
        idx = -1
        diff = 1000000
        for i, (mu, sig) in enumerate(zip(mus, sigs)):
            if abs(vol-sig) < diff:
                diff = abs(vol-sig)
                idx = i

        return mus[idx], sigs[idx]


    def plot_cov_matrix(self):
        #fig = px.density_heatmap(self.ef.cov_matrix)
        fig = px.imshow(self.ef.cov_matrix)
        return fig

    def plot_weights(self):

        opt_weights = [ self.opt_weights[ticker] for ticker in self.tickers ]
        curr_w = self.pf.get_weights()[-1,:]

        print(opt_weights)
        print(curr_w)

        diff_w = [ w1-w2 for w1, w2 in zip(curr_w, opt_weights) ]

        fig = go.Figure()

        fig.add_trace(go.Bar(y=self.tickers, x=opt_weights, name='Optimized', orientation='h'))
        fig.add_trace(go.Bar(y=self.tickers, x=curr_w, name='Current', orientation='h'))
        # fig.add_trace(go.Bar(x=self.tickers, y=diff_w, name='Diff'))

        # fig = px.bar(barmode='group')

        # fig, ax = plt.subplots(1,3)

        #curr_weights = { self.ef.tickers[i]: curr_w[0,i] for i in range(29) }
        # diffs = { ef.tickers[i]: curr_w[0,i] - cleaned_weights[ef.tickers[i]] for i in range(29) }

        # plotting.plot_weights(cleaned_weights,ax=ax[0])
        # plotting.plot_weights(curr_weights,ax=ax[1])
        # plotting.plot_weights(diffs, ax=ax[2])
        fig.update_layout(barmode='group')

        return fig

    def plot_optimization(self):

        fig = go.Figure()

        # Contour
        opt_ret, opt_sig = self.get_efficiency_frontier_contour()
        fig.add_trace(go.Scatter(x=opt_sig, y=opt_ret, name='Efficient frontier'))

        # Assets
        asset_ret, asset_sig = self.get_assets_performance()
        fig.add_trace(
            go.Scatter(
                x=asset_sig,
                y=asset_ret,
                mode='markers',
                marker={'size': 5, 'color': 'black'},
                name="Assets",
                hovertemplate='<b>%{text}</b>',
                text=[ f'{ticker}, {self.opt_weights[ticker]}' for ticker in self.tickers ],
            )
        )

        max_ret, max_sig= self.get_optmized_performance()
        fig.add_trace(
            go.Scatter(x=max_sig, y=max_ret,
                       mode='markers',
                       marker={'color': 'red', 'size': 10 },
                       name='Max sharpe'
                       )
        )

        # Generate random portfolios
        # fig.add_trace(go.Scatter(x=stds, y=rets,
        #                         mode='markers',
        #                         marker=dict(
        #                             size=5,
        #                             color=sharpes,
        #                             colorscale='Viridis', # one of plotly colorscales
        #                             showscale=True
        #                         ),
        #                         name='Random pfs'
        #     )
        # )

        curr_ret, curr_sig = self.get_current_portfolio_performance()
        fig.add_trace(
            go.Scatter(x=curr_sig, y=curr_ret,
                       mode='markers',
                       marker_symbol='x',
                       marker={'color': 'green', 'size': 10 },
                       name='Current portfolio'
                       )
        )


        # Same volatility
        samevol_ret, samevol_sig = self.get_optmized_with_current_volatility(opt_ret, opt_sig, curr_sig[0])
        fig.add_trace(
            go.Scatter(x=[samevol_sig,], y=[samevol_ret,],
                       mode='markers',
                       marker={'color': 'orange', 'size': 10 },
                       name='Same volatility'
                       )
        )

        # Same return
        sameret_ret, sameret_vol = self.get_optmized_with_current_return(curr_ret[0])
        fig.add_trace(
            go.Scatter(x=[sameret_vol,], y=[sameret_ret,],
                       mode='markers',
                       marker={'color': 'pink', 'size': 10 },
                       name='Same return'
                       )
        )


        fig.update_layout(
            template='simple_white',
            xaxis_title='Volatility',
            yaxis_title='Return',
        )

        return fig
