import plotly.express as px
import plotly.graph_objects as go

import pandas as pd

def plot_fraction_donut(data):

    data_tmp = data[['ticker', 'fraction']]

    # group stocks with fraction <1.5%
    try:
        data_tmp = pd.concat([
            data_tmp.loc[data_tmp["fraction"] >= 0.015],
            data_tmp.loc[data_tmp["fraction"] < 0.015].sum().to_frame().T,
        ])

        data_tmp['ticker'] = data_tmp['ticker'].apply(lambda x: '<1.5%' if len(x) > 6 else x)
    except:
        pass

    labels, values = data_tmp.ticker, data_tmp.fraction

    donut = go.Figure()
    #donut.layout.template = CHART_THEME
    donut.add_trace(go.Pie(labels=labels, values=values))
    donut.update_traces(hole=.5, hoverinfo="label+percent")
    donut.update_traces(textposition='outside', textinfo='none') ##label+percent')
    donut.update_layout(showlegend=True)
    donut.update_layout(margin = dict(t=50, b=50, l=25, r=25))
    #donut.show()

    return donut

def plot_fraction_sunburst(data):
    return px.sunburst(data, path=['kind', 'ticker'], values='fraction')

def plot_test(data):

    fig_growth2 = go.Figure()
    #fig_growth2.layout.template = CHART_THEME
    fig_growth2.add_trace(go.Bar(
        x=data.ticker,
        y=data.diff_pct,
        name='all'
    ))
    fig_growth2.add_trace(go.Bar(
        x=data.ticker,
        y=data.diff_pct_1m,
        name='1m',
    ))

    return fig_growth2

def plot_min_max(pfs):

    # Making a speedometer chart which indicates the stock' minimum and maximum closing prices
    # reached during the last 52 weeks along its current price.

    df_52_weeks_min = ambev.resample('W')['Close'].min()[-52:].min()
    df_52_weeks_max = ambev.resample('W')['Close'].max()[-52:].max()
    current_price = ambev.iloc[-1]['Close']

    fig = go.Figure()

    fig.add_trace(
        go.Indicator(
            mode='gauge+number', value=current_price,
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [df_52_weeks_min, df_52_weeks_max]},
                'bar': {'color': '#606bf3'}}
            )
    )

    fig.update_layout(
        title={'text': 'Min-Max Prices', 'y': 0.9},
        font={'size': 8},
        paper_bgcolor='black',
        font_color='grey',
        height=220,
        width=280,
        margin=dict(l=35, r=0, b=5, t=5),
        autosize=False,
        showlegend=False
    )

    return fig

def plot_evolution(pf, col, filter_str, title):

    fig = go.Figure()

    for ticker in pf.get_tickers(filter_str):

        try:
            df = pf.get_pfs().xs(ticker, level=1)
        except:
            continue

        s = go.Scatter(x=df.index, y=df[col], name=ticker)

        fig.add_trace(s)

        fig.update_layout(
            title=title
        )

    return fig


def plot_diff_vs_fraction(pf):

    # fig = go.Figure()

    # fig.add_trace(
    #     go.Scatter(x=pf.fraction,
    #                y=pf.diff_pp_1m,
    #                #color
    #                #size
    #                symbol=pf.kind,
    #                mode='markers',
    #                marker={'size': 5, 'color': 'black'},
    #                hovertemplate='<b>%{text}</b>',
    #                text=pf.ticker
    #                )
    # )

    fig = px.scatter(pf, x='fraction', y='diff_pct_1m', color='kind', text='ticker')
    fig.update_traces(textposition="bottom right")
    fig.update_layout(
        template='simple_white',
        xaxis_title='Fraction',
        yaxis_title='Diff % 1m',
    )

    fig.add_hline(y=0, line_width=1, line_dash="dash", line_color="gray")
    fig.add_hrect(y0=-0.01, y1=0.08, line_width=0, fillcolor="red", opacity=0.1)
    fig.add_hrect(y0=0.15, y1=0.4, line_width=0, fillcolor="green", opacity=0.1)

    # Add past points with a grey color?

    return fig


def plot_diff_vs_fraction_2(pf):

    fig = px.scatter(pf, x='diff_pct', y='diff_pct_1m', size='fraction', color='kind', text='ticker')
    fig.update_traces(textposition="bottom right")
    fig.update_layout(
        template='simple_white',
        xaxis_title='Diff %',
        yaxis_title='Diff % 1m',
    )

    fig.add_hline(y=0, line_width=1, line_dash="dash", line_color="gray")
    fig.add_hrect(y0=-0.01, y1=0.08, line_width=0, fillcolor="red", opacity=0.1)
    fig.add_hrect(y0=0.15, y1=0.4, line_width=0, fillcolor="green", opacity=0.1)

    return fig


def plot_diffs_3(pf):

    fig = px.scatter(pf, x='diff_pct_1m_usd', y='diff_pct_1m', size='fraction', color='kind', text='ticker')
    fig.update_traces(textposition="bottom right")
    fig.update_layout(
        template='simple_white',
        xaxis_title='Diff % 1m (USD)',
        yaxis_title='Diff % 1m (ARS)',
    )

    fig.add_hline(y=0, line_width=1, line_dash="dash", line_color="gray")
    fig.add_hrect(y0=-0.01, y1=0.08, line_width=0, fillcolor="red", opacity=0.1)
    fig.add_hrect(y0=0.15, y1=0.4, line_width=0, fillcolor="green", opacity=0.1)

    fig.add_vrect(x0=-0.05, x1=0, line_width=0, fillcolor="red", opacity=0.1)

    return fig
