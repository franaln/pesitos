import dash
from dash import dcc
from dash import html
#from dash import dash_table
from dash.dash_table import DataTable, FormatTemplate
from dash.dash_table.Format import Format, Group, Scheme, Symbol
from dash.dependencies import Input, Output
##from dash import Input, Output, State, html
import plotly.express as px
import plotly.graph_objects as go

import dash_bootstrap_components as dbc

from portfolio import Portfolio


portfolio = Portfolio()
portfolio.load()
portfolio.update()

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

#app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

# make a reuseable navitem for the different examples
#nav_item = dbc.NavItem(dbc.NavLink("Link", href="#"))

# make a reuseable dropdown for the different examples
# dropdown = dbc.DropdownMenu(
#     children=[
#         dbc.DropdownMenuItem("Entry 1"),
#         dbc.DropdownMenuItem("Entry 2"),
#         dbc.DropdownMenuItem(divider=True),
#         dbc.DropdownMenuItem("Entry 3"),
#     ],
#     nav=True,
#     in_navbar=True,
#     label="Menu",
# )

nav_items = [
    dbc.NavItem(dbc.NavLink("Now",       href="/page-now")),
    dbc.NavItem(dbc.NavLink("Board",       href="/page-board")),
    dbc.NavItem(dbc.NavLink("Evolution", href="/page-evolution")),
    dbc.NavItem(dbc.NavLink("Market",    href="/page-market")),
]

navbar = dbc.NavbarSimple(
    children=nav_items,
    brand='Pesitos',
    brand_href='#',
    color="dark",
    dark=True,
    className="mb-5",
)

# CSS style
style = {
    'backgroundColor': '#444654',
    'faceColor': '#fffff',
    'textColor': '#fffff',
    'textAlign': 'center',
    'fontFamily': 'Roboto',
    'padding': '10px',
}

table_style = {
    'font-family': 'Roboto',
    'font-size': '14px',
}


content = html.Div(id='page-content')

# Layout
app.layout = html.Div(
    style=style,
    children=[
        dcc.Location(id='url'),
        dcc.Interval(
            id='interval-component',
            interval=30 * 60 * 1000,  # Intervalo de actualización: 30 minutos en milisegundos
            n_intervals=0
        ),
        navbar,
        content,
])

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    Input('interval-component', 'n_intervals')
)
def render_page_content(pathname, n):

    print(' *** ', pathname, n)

    if pathname == '/page-now':

        # Actualizar el DataFrame cada media hora
        if n and n % 30 == 0:
            portfolio.update()

        fmt_p = {
            "specifier": ".2f",
        }

        fmt_perc = FormatTemplate.percentage(2)

        columns = [
            dict(id='ticker',   name='Ticker'  ),
            dict(id='n',        name='N',        type='numeric'),
            dict(id='ppc',      name='PPC',      type='numeric', format=fmt_p),
            dict(id='days_avg', name='Days',     type='numeric'),
            dict(id='total_ar', name='Total',    type='numeric', format=fmt_p),
            dict(id='price_ar', name='Price AR', type='numeric', format=fmt_p),
            dict(id='price_us', name='Price US', type='numeric', format=fmt_p),
            
            dict(id='price_ar_change_1d', name='Change AR %', type='numeric', format=fmt_perc),
            dict(id='price_us_change_1d', name='Change US %', type='numeric', format=fmt_perc),

            dict(id='ccl', name='CCL', type='numeric', format=fmt_p),
            dict(id='total_ar_now', name='Total Now', type='numeric', format=fmt_p),
            dict(id='diff', name='Diff', type='numeric', format=fmt_p),
            #dict(id='diff_unit_pp', name='Diff unit %', type='numeric', format=fmt_perc),
            dict(id='diff_pp', name='Diff %', type='numeric', format=fmt_perc),
            dict(id='diff_pp_1mo', name='Diff % 1mo', type='numeric', format=fmt_perc),

            dict(id='fraction', name='Fraction', type='numeric', format=fmt_perc),
            # dict(id='balance', name='Balance', type='numeric', format=money),
            # dict(id='rate', name='Rate', type='numeric', format=percentage)
        ]

        data = portfolio.dbm.to_dict('records')

        #print(data)

        table = DataTable(
            id='tbl',
            columns=columns,
            data=data,

            filter_action='native',
            sort_action='native',
            sort_mode='multi',
            column_selectable='multi',
            row_selectable='multi',
            selected_columns=[],
            selected_rows=[],
            style_table={'overflowX': 'auto', **table_style},
            style_cell={
                #'backgroundColor': '#444654',
                #'color': '#ffffff',
                'textAlign': 'right',
                'padding': '5px',
                'minWidth': '30px', 'width': '80px', 'maxWidth': '80px',  # Define el ancho de las celdas
                'whiteSpace': 'normal',  # Permite que el contenido de las celdas se ajuste automáticamente
                **table_style
            },
            style_header={
                #'backgroundColor': '#111111',
                #'color': '#ffffff',
                **table_style
            },
            style_data_conditional=[
                {
                    'if': {
                        'filter_query': '{diff_pp_1mo} > 0.10 && {diff_pp_1mo} < 0.25',
                        'column_id': 'diff_pp_1mo',
                    },
                    'backgroundColor': '#e5890b',
                    'color': 'white'
                },
                { 'if': { 
                    'filter_query': '{diff_pp_1mo} > 0.25', 
                    'column_id': 'diff_pp_1mo'
                    }, 
                    'backgroundColor': 'tomato',
                    'color': 'blue' 
                },
                {
                    'if': { 'filter_query': '{price_ar_change_1d} > 0', 'column_id': 'price_ar_change_1d'},
                    'color': 'green'
                },
                {
                    'if': { 'filter_query': '{price_ar_change_1d} < 0', 'column_id': 'price_ar_change_1d'},
                    'color': 'tomato'
                },
                
            ]
        )

        return html.Div([table])
    
    elif pathname == '/page-board':

        labels = portfolio.dbm.ticker
        values = portfolio.dbm.fraction

        #donut_top = go.Figure()
        #donut_top.layout.template = CHART_THEME
        #donut_top.add_trace(go.Pie(labels=labels, values=values))
        #donut_top.update_traces(hole=.5, hoverinfo="label+percent")
        #donut_top.update_traces(textposition='outside', textinfo='label+percent')
        #donut_top.update_layout(showlegend=False)
        #donut_top.update_layout(margin = dict(t=50, b=50, l=25, r=25))
        #donut_top.show()

        donut_top = px.sunburst(portfolio.dbm, path=['kind', 'ticker'], values='fraction')

        fig_growth2 = go.Figure()
        #fig_growth2.layout.template = CHART_THEME
        fig_growth2.add_trace(go.Bar(
            x=labels,
            y=portfolio.dbm.diff_pp,
            name='all'
        ))
        fig_growth2.add_trace(go.Bar(
            x=labels,
            y=portfolio.dbm.diff_pp_1mo,
            name='1mo',
        ))
        #fig_growth2.update_layout(barmode='group')
        # fig_growth2.layout.height=300
        # fig_growth2.update_layout(margin = dict(t=50, b=50, l=25, r=25))
        # fig_growth2.update_layout(
        #     xaxis_tickfont_size=12,
        #     yaxis=dict(
        #         title='% change',
        #         titlefont_size=13,
        #         tickfont_size=12,
        #     ))
            
        #     fig_growth2.update_layout(legend=dict(
        #         yanchor="top",
        #         y=0.99,
        #         xanchor="right",
        #         x=0.99))
        #         fig_growth2.show()
                
        print('donut')
        return html.Div([
            dbc.Card([
                dcc.Graph(id='pie-top15',
                figure=donut_top,
                style={'height':380})
            ]),
            dbc.Card([
                dcc.Graph(id='1',
                          figure=fig_growth2)
            ])
        ])
        # ,
        #     width={'size': 4, 'offset': 0, 'order': 2}
        # )
    
        #dbc.Card([dbc.CardHeader(add_help(html.H6('Created by'), 'created')), html.Div(id='created-by2')], className='col-md-3'),
        #     dbc.Card(
        #         dbc.Col([
        #         dbc.Row([
        #             dcc.DatePickerRange(id='date-picker2', display_format='DD/MM/YYYY', clearable=True),
        #             dbc.Col(
        #                 dcc.Dropdown(id='dropdown-users2', placeholder='Filter user', options=[], multi=True, value=[]), style={'margin-left': '20px', 'margin-right': '20px'}),
        #             #html.Div(['Show help :', daq.BooleanSwitch(id='help-switch', on=False, color='#29b6f6', style={'margin-left': '5px'})], style={'margin-left': 'auto', 'margin-right': '0px', 'display': 'inherit'})
        #         ], align='center')
        #     ]), className='card-filter'),])

    else:
        print('else')
        return None


# @app.callback(
#     Output('tbl', 'style_data_conditional'),
#     Input('tbl', 'selected_columns')
# )
# def update_styles(selected_columns):
#     return [{
#         'if': { 'column_id': i },
#         'background_color': '#D2F3FF'
#     } for i in selected_columns]




# @app.callback(
#     [
#         dash.dependencies.Output('portfolio-graph', 'figure'),
#         dash.dependencies.Output('other-graph', 'figure')
#     ],
#     [dash.dependencies.Input('interval-component', 'n_intervals')]
# )
# def update_graphs(n):
#     # Aquí puedes agregar la lógica para actualizar los gráficos según sea necesario
#     # Por ejemplo, puedes filtrar los datos para un rango de fechas actualizado

#     # Crear gráfico de portfolio
#     portfolio_fig = px.line(df_p, x='Ticker', y='Total')

#     # Crear otro gráfico
#     #other_fig = px.bar(...)

#     return portfolio_fig, other_fig


if __name__ == '__main__':
    app.run_server(debug=True)
