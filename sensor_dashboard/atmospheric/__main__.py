from sensor_dashboard.connection import get_queried_df
from atmospheric import (
    create_temp_plot, create_pressure_plot, create_humidity_plot
)
from dash import Dash, html, dcc, Output, Input, callback

app = Dash(__name__)
app.layout = html.Div([
    html.H1(id='atmospheric',
            children='Atmospheric Data',
            style={'textAlign': 'center'}),
    dcc.Interval(id='interval', interval=1000 * 1),

    html.H2(children='Temperature(degrees Celsius)', style={'textAlign': 'left'}),
    dcc.Graph(id='temp_fig'),

    html.H2(children='Atmospheric Pressure (mPascals)', style={'textAlign': 'left'}),
    dcc.Graph(id='pressure_fig'),

    html.H2(children='Relative Humidity', style={'textAlign': 'left'}),
    dcc.Graph(id='humidity_fig'),
])

@callback(
    Output('temp_fig', 'figure'),
    Output('pressure_fig', 'figure'),
    Output('humidity_fig', 'figure'),
    Input('interval', 'n_intervals'),
)
def update_from_database(interval):
    df = get_queried_df()
    temp_fig = create_temp_plot(df)
    pressure_fig = create_pressure_plot(df)
    humidity_fig = create_humidity_plot(df)
    return temp_fig, pressure_fig, humidity_fig

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)