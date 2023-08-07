from dash.dash_table import FormatTemplate

# CSS style
style = {
    'backgroundColor': '#444654',
    'faceColor': '#fffff',
    'textColor': '#fffff',
    'textAlign': 'center',
    'fontFamily': 'Roboto',
    'padding': '10px',
}

style_table = {
    'overflowX': 'auto',
    'font-family': 'Roboto',
    'font-size': '14px',
}

fmt_p = {
    "specifier": ".2f",
}

fmt_perc = FormatTemplate.percentage(2)

style_table_cell = {
    #'backgroundColor': '#444654',
    #'color': '#ffffff',
    'textAlign': 'right',
    'padding': '5px',
    'minWidth': '30px', 'width': '60px', 'maxWidth': '60px',  # Define el ancho de las celdas
    'whiteSpace': 'normal',  # Permite que el contenido de las celdas se ajuste automáticamente
    **style_table
}

style_table_header = {
    #'backgroundColor': '#111111',
    #'color': '#ffffff',
    **style_table
}


c_green = 'DarkSeaGreen'
c_red   = 'LightCoral'

# scale 
c_p1 = 'Tomato'
c_p2 = 'LightCoral'
c_p3 = 'LightPink'
c_p4 = 'LightGreen'
c_p5 = 'DarkSeaGreen'
c_p6 = 'MediumSeaGreen'
