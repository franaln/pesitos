import dash
from dash import dcc
from dash import html
from dash.dash_table import DataTable, FormatTemplate
from dash.dash_table.Format import Format, Group, Scheme, Symbol
from dash.dependencies import Input, Output

import dash_bootstrap_components as dbc

from style import *
from plots import *
from portfolio import Portfolio
from optimization import Optimization

#
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

pf = Portfolio()


fmt_ars = {'locale': {}, 'nully': '', 'prefix': 1000, 'specifier': '$.2r'}

nav_items = [
    # dbc.NavItem(dbc.NavLink("Summary",   href="/page-summary")),
    dbc.NavItem(dbc.NavLink("Portfolio", href="/page-portfolio")),
    dbc.NavItem(dbc.NavLink("Board",     href="/page-board")),
    dbc.NavItem(dbc.NavLink("Evolution", href="/page-evolution")),
    dbc.NavItem(dbc.NavLink("Optimization", href="/page-optimization")),

    dbc.Button(['Update'], color='primary', id='btn-update')
]

navbar = dbc.NavbarSimple(
    children=nav_items,
    brand='[Pesito$]',
    brand_href='#',
    color="dark",
    dark=True,
    className="mb-5",
)


def serve_layout():
    return html.Div(
        style=style,
        children=[
            dcc.Location(id='url'),
            dcc.Interval(
                id='interval-component',
                interval=60 * 1000 * 1000, # (1000m tmp, remove 1000 later) 1m
                n_intervals=0
            ),
            navbar,
            html.Div(id='update-label'),
            html.Div(children=[html.P(pf.date)], id='page-content'),
        ])

app.layout = serve_layout

fmt_perc = FormatTemplate.percentage(2)

table_format_conditions = [

    # diff % 1m ARS
    {
        'if': {
            'filter_query': '{diff_pct_1m} < 0',
            'column_id': 'diff_pct_1m',
        },
        'backgroundColor': c_p1
    },
    {
        'if': {
            'filter_query': '{diff_pct_1m} > 0 && {diff_pct_1m} < 0.08',
            'column_id': 'diff_pct_1m',
        },
        'backgroundColor': c_p2
    },
    {
        'if': {
            'filter_query': '{diff_pct_1m} > 0.08 && {diff_pct_1m} < 0.10',
            'column_id': 'diff_pct_1m',
        },
        'backgroundColor': c_p3
    },
    {
        'if': {
            'filter_query': '{diff_pct_1m} > 0.10 && {diff_pct_1m} < 0.20',
            'column_id': 'diff_pct_1m',
        },
        'backgroundColor': c_p4
    },
    {
        'if': {
            'filter_query': '{diff_pct_1m} > 0.2',
            'column_id': 'diff_pct_1m'
        },
        'backgroundColor': c_p5
    },
    {
        'if': {
            'filter_query': '{diff_pct_1m} > 0.3',
            'column_id': 'diff_pct_1m'
        },
        'backgroundColor': c_p6
    },


    # diff 1m USD
    {
        'if': {
            'filter_query': '{diff_pct_1m_usd} < 0',
            'column_id': 'diff_pct_1m_usd',
        },
        'backgroundColor': c_p1
    },
    {
        'if': {
            'filter_query': '{diff_pct_1m_usd} > 0 && {diff_pct_1m_usd} < 0.08',
            'column_id': 'diff_pct_1m_usd',
        },
        'backgroundColor': c_p2
    },
    {
        'if': {
            'filter_query': '{diff_pct_1m_usd} > 0.08 && {diff_pct_1m_usd} < 0.10',
            'column_id': 'diff_pct_1m_usd',
        },
        'backgroundColor': c_p3
    },
    {
        'if': {
            'filter_query': '{diff_pct_1m_usd} > 0.10 && {diff_pct_1m_usd} < 0.20',
            'column_id': 'diff_pct_1m_usd',
        },
        'backgroundColor': c_p4
    },
    {
        'if': {
            'filter_query': '{diff_pct_1m_usd} > 0.2',
            'column_id': 'diff_pct_1m_usd'
        },
        'backgroundColor': c_p5
    },
    {
        'if': {
            'filter_query': '{diff_pct_1m_usd} > 0.3',
            'column_id': 'diff_pct_1m_usd'
        },
        'backgroundColor': c_p6
    },


    # Price last change
    {
        'if': {
            'filter_query': '{price_ar_change_1d} > 0',
            'column_id': 'price_ar_change_1d'
        },
        'backgroundColor': c_green
    },
    {
        'if': {
            'filter_query': '{price_ar_change_1d} < 0',
               'column_id': 'price_ar_change_1d'
        },
        'backgroundColor': c_red
    },
    {
        'if': {
            'filter_query': '{price_us_change_1d} > 0',
            'column_id': 'price_us_change_1d'
        },
        'backgroundColor': c_green
    },
    {
        'if': {
            'filter_query': '{price_us_change_1d} < 0',
            'column_id': 'price_us_change_1d'
        },
        'backgroundColor': c_red
    },
    # {
    #     'if': {
    #         'filter_query': '{diff_pct} > 0',
    #         'column_id': 'diff_pct'
    #     },
    #     'backgroundColor': c_green
    # },
    # {
    #     'if': {
    #         'filter_query': '{diff_pct} < 0',
    #         'column_id': 'diff_pct'
    #     },
    #     'backgroundColor': c_red
    # },
]

#
@app.callback(
    Output('update-label', 'children'), [Input("btn-update", "n_clicks")]
)
def on_button_click(n):
    if n is None:
        return None
    else:
        pf.update_current_portfolio()
        return html.Div([html.P(pf.date)])








## Pages
# def get_page_summary():

#     # Total table
#     columns_total = [
#         dict(id='total_ar', name='Total',    type='numeric', format=fmt_p),
#         dict(id='total_ar_now', name='Total Now', type='numeric', format=fmt_p),
#         dict(id='diff', name='Diff', type='numeric', format=fmt_p),
#         dict(id='diff_pp', name='Diff %', type='numeric', format=fmt_perc),
#         dict(id='diff_pp_1d', name='Diff 1d %', type='numeric', format=fmt_perc),
#         dict(id='diff_pp_1w', name='Diff 1w %', type='numeric', format=fmt_perc),
#         dict(id='diff_pp_1m', name='Diff 1m %', type='numeric', format=fmt_perc),
#         dict(id='diff_pp_1y', name='Diff 1y %', type='numeric', format=fmt_perc),
#     ]

#     columns = [
#         dict(id='ticker',   name='Ticker'  ),
#         dict(id='n',        name='N',        type='numeric'),
#         dict(id='price_ar', name='Price AR', type='numeric', format=fmt_p),
#         dict(id='price_us', name='Price US', type='numeric', format=fmt_p),
#         dict(id='price_ar_change_1d', name='Change AR %', type='numeric', format=fmt_perc),
#         dict(id='price_us_change_1d', name='Change US %', type='numeric', format=fmt_perc),
#         dict(id='diff_pp', name='Diff %', type='numeric', format=fmt_perc),
#         dict(id='diff_pp_1m', name='Diff % 1m', type='numeric', format=fmt_perc),
#         dict(id='fraction', name='Fraction', type='numeric', format=fmt_perc),
#     ]

#     data = pf.get_dict()

#     # Add total table
#     # Fix some values

#     # if price_ar < 0.0001:
#     #     price_ar = (500 * price_us) / ratio

#     table = DataTable(
#         id='tbl-summary',
#         columns=columns,
#         data=data,
#         filter_action='native',
#         sort_action='native',
#         sort_mode='multi',
#         column_selectable='multi',
#         style_table=style_table,
#         style_cell=style_table_cell,
#         style_header=style_table_header,
#         style_data_conditional=table_format_conditions,
#     )

#     table_total = DataTable(
#         id='tbl-total',
#         columns=columns_total,
#         data=[pf.get_total_dict(),],
#         style_table=style_table,
#         style_cell=style_table_cell,
#         style_header=style_table_header,
#     )

#     return html.Div([table_total, table])


def get_page_portfolio():

    columns_total = [
        dict(id='total',     name='Total',        type='numeric', format=fmt_ars),
        dict(id='total_now', name='Total Now',    type='numeric', format=fmt_ars),
        dict(id='total_usd',     name='Total USD',     type='numeric', format=fmt_p),
        dict(id='total_now_usd', name='Total USD Now', type='numeric', format=fmt_p),

        dict(id='diff', name='Diff', type='numeric', format=fmt_ars),
        dict(id='diff_pct', name='Diff %', type='numeric', format=fmt_perc),

        dict(id='diff_usd',    name='Diff USD',   type='numeric', format=fmt_p),
        dict(id='diff_pct_usd', name='Diff USD %', type='numeric', format=fmt_perc),
    ]

    columns = [
        dict(id='ticker',   name='Ticker'  ),
        dict(id='n',        name='N',        type='numeric'),
        dict(id='ppc',      name='PPC',      type='numeric', format=fmt_p),
        dict(id='days', name='Days',     type='numeric'),
        dict(id='total', name='Total',    type='numeric', format=fmt_p),
        dict(id='total_usd', name='Total USD',    type='numeric', format=fmt_p),

        dict(id='price_ar', name='Price AR', type='numeric', format=fmt_p),
        dict(id='price_us', name='Price US', type='numeric', format=fmt_p),

        dict(id='price_ar_change_1d', name='Change AR %', type='numeric', format=fmt_perc),
        dict(id='price_us_change_1d', name='Change US %', type='numeric', format=fmt_perc),
        dict(id='ccl', name='CCL', type='numeric', format=fmt_p),

        dict(id='total_now', name='Total Now', type='numeric', format=fmt_p),
        dict(id='diff', name='Diff', type='numeric', format=fmt_p),

        dict(id='total_now_usd', name='Total Now', type='numeric', format=fmt_p),
        dict(id='diff_usd', name='Diff', type='numeric', format=fmt_p),

        #dict(id='diff_unit_pp', name='Diff unit %', type='numeric', format=fmt_perc),
        dict(id='diff_pct', name='Diff %', type='numeric', format=fmt_perc),
        dict(id='diff_pct_usd', name='Diff %', type='numeric', format=fmt_perc),

        # dict(id='diff_pct_1d', name='Diff 1d %', type='numeric', format=fmt_perc),
        # dict(id='diff_pct_1w', name='Diff 1w %', type='numeric', format=fmt_perc),
        dict(id='diff_pct_1m', name='Diff 1m %', type='numeric', format=fmt_perc),
        # dict(id='diff_pct_1y', name='Diff 1y %', type='numeric', format=fmt_perc),

        dict(id='diff_pct_1m_usd', name='Diff 1m %', type='numeric', format=fmt_perc),

        dict(id='fraction', name='Fraction', type='numeric', format=fmt_perc),
        # dict(id='balance', name='Balance', type='numeric', format=money),
        # dict(id='rate', name='Rate', type='numeric', format=percentage)
    ]

    data = pf.get_dict()

    # Add total table
    # Fix some values

    # if price_ar < 0.0001:
    #     price_ar = (500 * price_us) / ratio

    table_total = DataTable(
        id='tbl_total',
        columns=columns_total,
        data=[pf.get_total_dict(),],
        #filter_action='native',
        #sort_action='native',
        #sort_mode='multi',
        #column_selectable='multi',
        #row_selectable='multi',
        #selected_columns=[],
        #selected_rows=[],
        style_table=style_table,
        style_cell=style_table_cell,
        style_header=style_table_header,
        #style_data_conditional=table_format_conditions,
    )

    table = DataTable(
        id='tbl',
        columns=columns,
        data=data,
        filter_action='native',
        sort_action='native',
        sort_mode='multi',
        # column_selectable='multi',
        # row_selectable='multi',
        # selected_columns=[],
        # selected_rows=[],
        style_table=style_table,
        style_cell=style_table_cell,
        style_header=style_table_header,
        style_data_conditional=table_format_conditions,
    )

    return html.Div([table_total, table])


def get_page_board():
    return html.Div([
        dbc.Row([
            dcc.Graph(id='board-p1',
                      figure=plot_fraction_donut(pf.get_data()),
                      style={'width': 350, 'height': 350}),
            dcc.Graph(id='board-p2',
                      figure=plot_fraction_sunburst(pf.get_data()),
                      style={'width': 350, 'height': 350}
                      )
        ]),
        dbc.Card([
            dcc.Graph(id='1',
                      figure=plot_test(pf.get_data()))
        ]),
        dcc.Graph(id='board-p3', figure=plot_diff_vs_fraction(pf.get_data()), config={'displayModeBar': False}),
        dcc.Graph(id='board-p4', figure=plot_diff_vs_fraction_2(pf.get_data()), config={'displayModeBar': False}),
        dcc.Graph(id='board-p5', figure=plot_diffs_3(pf.get_data()), config={'displayModeBar': False}),
    ])


def get_page_evolution():

    filter_AR  = 'kind=="AR"'
    filter_CAR = '(kind=="CAR") & (fraction>0.015)'

    return html.Div(
        [
            dcc.Graph(id='pp', figure=plot_evolution(pf, 'diff_pct_1m', filter_AR,  'diff_pct_1m, AR')),
            dcc.Graph(id='pp', figure=plot_evolution(pf, 'diff_pct_1m', filter_CAR, 'diff_pct_1m, CAR')),

            dcc.Graph(id='pp', figure=plot_evolution(pf, 'diff_pct', filter_AR, 'diff_pp, AR')),
            dcc.Graph(id='pp', figure=plot_evolution(pf, 'diff_pct', filter_CAR, 'diff_pp, CAR')),

            # dcc.Graph(id='pp', figure=plot_evolution(pf, 'n')),
            # dcc.Graph(id='pp', figure=plot_evolution(pf, 'total_ar')),

            dcc.Graph(id='pp', figure=plot_evolution(pf, 'total_now', filter_AR, 'total, AR')),
            dcc.Graph(id='pp', figure=plot_evolution(pf, 'total_now', filter_CAR, 'total, CAR')),

            # dcc.Graph(id='pp', figure=plot_evolution(pf, 'fraction')),
        ]
    )

def get_page_optimization():

    opt = Optimization(pf)
    opt.optimize()

    return html.Div([
        dcc.Graph(id='x', figure=opt.plot_optimization()),

        dcc.Graph(id='xx',
                  figure=opt.plot_weights(),
                  style={'width': 500, 'height': 1000}),

        dcc.Graph(id='xxx',
                  figure=opt.plot_cov_matrix(),
                  style={'width': 500, 'height': 500}),


    ])


@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    Input('interval-component', 'n_intervals')
)
def render_page_content(pathname, n):

    # Actualizar el DataFrame cada media hora
    # if n % 15 == 0:
        # print(f'*** ({n=}) Updating portfolio...')
        # pf.update()

    print(f'[Dashboard] render page content: page={pathname}, interval={n}')

    # if pathname == '/page-summary':
    #     return get_page_summary()
    if pathname == '/page-portfolio':
        return get_page_portfolio()
    elif pathname == '/page-board':
        return get_page_board()
    elif pathname == '/page-evolution':
        return get_page_evolution()
    elif pathname == '/page-optimization':
        return get_page_optimization()

    else:
        print('else')
        return None

# @app.callback(Output('badge', 'children'), Input('button', 'n_clicks'))
# def on_button_click(n):
    # pf.update()
    # return f'({pf.get_date()})'


if __name__ == '__main__':
    app.run_server(port=8050, host='127.0.0.1', debug=True)
