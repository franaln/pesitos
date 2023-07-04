import dash
from dash import dcc
from dash import html
#from dash import dash_table
from dash.dash_table import DataTable, FormatTemplate
from dash.dash_table.Format import Format, Group, Scheme, Symbol
from dash.dependencies import Input, Output
##from dash import Input, Output, State, html
import plotly.express as px

import dash_bootstrap_components as dbc

from portfolio import Portfolio


portfolio = Portfolio()
portfolio.load()

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

#app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

# make a reuseable navitem for the different examples
#nav_item = dbc.NavItem(dbc.NavLink("Link", href="#"))

# make a reuseable dropdown for the different examples
dropdown = dbc.DropdownMenu(
    children=[
        dbc.DropdownMenuItem("Entry 1"),
        dbc.DropdownMenuItem("Entry 2"),
        dbc.DropdownMenuItem(divider=True),
        dbc.DropdownMenuItem("Entry 3"),
    ],
    nav=True,
    in_navbar=True,
    label="Menu",
)

# this is the default navbar style created by the NavbarSimple component
# default = dbc.NavbarSimple(
#     children=[nav_item, dropdown],
#     brand="Default",
#     brand_href="#",
#     sticky="top",
#     className="mb-5",
# )

# here's how you can recreate the same thing using Navbar
# (see also required callback at the end of the file)
# custom_default = dbc.Navbar(
#     dbc.Container(
#         [
#             dbc.NavbarBrand("Custom default", href="#"),
#             dbc.NavbarToggler(id="navbar-toggler1"),
#             dbc.Collapse(
#                 dbc.Nav(
#                     [nav_item, dropdown], className="ms-auto", navbar=True
#                 ),
#                 id="navbar-collapse1",
#                 navbar=True,
#             ),
#         ]
#     ),
#     className="mb-5",
# )


# this example that adds a logo to the navbar brand
navbar = dbc.Navbar(
    dbc.Container(
        [
            dbc.NavbarBrand('Pesitos', href='#'),
            # html.A(
            #     # Use row and col to control vertical alignment of logo / brand
            #     dbc.Row(
            #         [
            #             #dbc.Col(html.Img(src=PLOTLY_LOGO, height="30px")),
            #             dbc.Col(dbc.NavbarBrand("Pesitos", className="ms-2")),
            #         ],
            #         align="center",
            #         className="g-0",
            #     ),
            #     href="https://plotly.com",
            #     style={"textDecoration": "none"},
            # ),
            dbc.NavbarToggler(id="navbar-toggler2", n_clicks=0),
            dbc.Collapse(
                dbc.Nav(
                    [
                        dbc.NavItem(dbc.NavLink("Now",       href="#")),
                        dbc.NavItem(dbc.NavLink("Evolution", href="#")),
                        dbc.NavItem(dbc.NavLink("Market",    href="#")),
                        dropdown, 
                     ],
                    className="ms-auto",
                    navbar=True,
                ),
                id="navbar-collapse",
                navbar=True,
            ),
        ],
    ),
    color="dark",
    dark=True,
    className="mb-5",
)

# # this example has a search bar and button instead of navitems / dropdowns
# search_navbar = dbc.Navbar(
#     dbc.Container(
#         [
#             dbc.NavbarBrand("Search", href="#"),
#             dbc.NavbarToggler(id="navbar-toggler3"),
#             dbc.Collapse(
#                 dbc.Row(
#                     [
#                         dbc.Col(
#                             dbc.Input(type="search", placeholder="Search")
#                         ),
#                         dbc.Col(
#                             dbc.Button(
#                                 "Search", color="primary", className="ms-2"
#                             ),
#                             # set width of button column to auto to allow
#                             # search box to take up remaining space.
#                             width="auto",
#                         ),
#                     ],
#                     # add a top margin to make things look nice when the navbar
#                     # isn't expanded (mt-3) remove the margin on medium or
#                     # larger screens (mt-md-0) when the navbar is expanded.
#                     # keep button and search box on same row (flex-nowrap).
#                     # align everything on the right with left margin (ms-auto).
#                     className="g-0 ms-auto flex-nowrap mt-3 mt-md-0",
#                     align="center",
#                 ),
#                 id="navbar-collapse3",
#                 navbar=True,
#             ),
#         ]
#     ),
#     className="mb-5",
# )

# # custom navbar based on https://getbootstrap.com/docs/4.1/examples/dashboard/
# dashboard = dbc.Navbar(
#     dbc.Container(
#         [
#             dbc.Col(dbc.NavbarBrand("Dashboard", href="#"), sm=3, md=2),
#             dbc.Col(dbc.Input(type="search", placeholder="Search here")),
#             dbc.Col(
#                 dbc.Nav(
#                     dbc.Container(dbc.NavItem(dbc.NavLink("Sign out"))),
#                     navbar=True,
#                 ),
#                 width="auto",
#             ),
#         ],
#     ),
#     color="dark",
#     dark=True,
# )

# app.layout = html.Div(
#     [default, custom_default, logo, search_navbar, dashboard]
# )


# # we use a callback to toggle the collapse on small screens
# def toggle_navbar_collapse(n, is_open):
#     if n:
#         return not is_open
#     return is_open


# # the same function (toggle_navbar_collapse) is used in all three callbacks
# for i in [1, 2, 3]:
#     app.callback(
#         Output(f"navbar-collapse{i}", "is_open"),
#         [Input(f"navbar-toggler{i}", "n_clicks")],
#         [State(f"navbar-collapse{i}", "is_open")],
#     )(toggle_navbar_collapse)

# if __name__ == "__main__":
#     app.run_server(debug=True, port=8888)


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

# Layout
app.layout = html.Div(
    style=style,
    children=[
        #default,
        #custom_default,
        navbar,
        #search_navbar,
        #dashboard,
        #html.H1('Pesitos'),
        dcc.Tabs(id='tabs', ##value='tab-1',
                 children=[
                     dcc.Tab(label='Now',       value='tab-1'),
                     dcc.Tab(label='Evolution', value='tab-2'),
                     dcc.Tab(label='Market',    value='tab-3'),
                 ]),
        html.Div(id='content'),
        dcc.Interval(
            id='interval-component',
            interval=30 * 60 * 1000,  # Intervalo de actualización: 30 minutos en milisegundos
            n_intervals=0
        )

        # dcc.Tabs(id='tabs', value='tab-1', children=[
        #     dcc.Tab(label='Tab 1', value='tab-1'),
        #     dcc.Tab(label='Tab 2', value='tab-2')
        # ]),
        # html.Div(id='content'),
        # html.Button('Botón 1', id='button-1', n_clicks=0),
        # html.Button('Botón 2', id='button-2', n_clicks=0),
        # html.Div(id='output'),
    # dcc.Graph(id='portfolio-graph'),
    # dcc.Graph(id='other-graph')
])

@app.callback(
    Output('content', 'children'),
    Input('tabs', 'value'),
    Input('navbar-collapse', 'value'),
    Input('interval-component', 'n_intervals')
)
def update_table(tab, navbar_tab, n):

    portfolio.update()

    print(navbar_tab)

    if tab == 'tab-1':

        # Actualizar el DataFrame cada media hora
        if n and n % 30 == 0:
            portfolio.update()

        fmt_p = {  # formatted "manually"
            "specifier": ".2f",
        }

        fmt_perc = FormatTemplate.percentage(2)
        #'specifier':
        # "locale": {
        #     "symbol": ["€", " EUR"],
        #     "group": ".",
        #     "decimal": ",",
        # },

        columns = [
            dict(id='ticker',   name='Ticker'  ),
            dict(id='n',        name='N',        type='numeric'),
            dict(id='ppc',      name='PPC',      type='numeric', format=fmt_p),
            dict(id='days_avg', name='Days',     type='numeric'),
            dict(id='total_ar', name='Total',    type='numeric', format=fmt_p),
            dict(id='price_ar', name='Price AR', type='numeric', format=fmt_p),
            dict(id='price_us', name='Price US', type='numeric', format=fmt_p),
            
            #dict(id='price_ar_change_1d', name='Change AR %', type='numeric', format=fmt_perc),
            #dict(id='price_us_change_1d', name='Change US %', type='numeric', format=fmt_perc),

            #dict(id='ccl', name='CCL', type='numeric', format=fmt_p),
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

        #data.append(portfolio.total_dict)

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
                'minWidth': '40px', 'width': '80px', 'maxWidth': '80px',  # Define el ancho de las celdas
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
                        'column_id': 'diff_pp_1mo',
                        'filter_query': '{diff_pp_1mo} > 10'
                    },
                    'backgroundColor': 'dodgerblue',
                    'color': 'white'
                },
            ]
        )

        return html.Div([table])

    else:
        return None


@app.callback(
    Output('tbl', 'style_data_conditional'),
    Input('tbl', 'selected_columns')
)
def update_styles(selected_columns):
    return [{
        'if': { 'column_id': i },
        'background_color': '#D2F3FF'
    } for i in selected_columns]


# Iniciar el intervalo de actualización
@app.callback(Output('interval-component', 'n_intervals'),
              Input('tabs', 'value'))
def reset_interval(n):
    return 0

# @app.callback(
#     Output('content', 'children'),
#     Input('tabs', 'value')
# )
# def render_content(tab):
#     if tab == 'tab-1':
#         return html.Div([
#             html.H2('Contenido de la Pestaña 1')
#         ])
#     elif tab == 'tab-2':
#         return html.Div([
#             html.H2('Contenido de la Pestaña 2')
#         ])

# @app.callback(
#     Output('output', 'children'),
#     [Input('button-1', 'n_clicks'), Input('button-2', 'n_clicks')]
# )
# def update_output(btn1_clicks, btn2_clicks):
#     return f'Botón 1 ha sido clickeado {btn1_clicks} veces. Botón 2 ha sido clickeado {btn2_clicks} veces.'


# # app.layout = html.Div([
# #     html.H1('Dashboard de Portfolio de Stocks'),
# # ])


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
