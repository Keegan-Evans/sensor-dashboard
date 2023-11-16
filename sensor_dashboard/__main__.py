from datetime import date, datetime

from sensor_dashboard.connection import get_queried_df
from sensor_dashboard.munge_and_plot import (
    create_wind_polar_plot, munge_wind_data, create_wind_speed_plot,
    create_rainfall_plot,
)

from sensor_dashboard.atmospheric import (
    create_temp_plot, create_pressure_plot, create_humidity_plot
)

from dash import Dash, html, dcc, Output, Input, callback


app = Dash(__name__)
app.layout = html.Div([

    html.H1(id='weather_station',
            children='Weather Station Data',
            style={'textAlign': 'center'}),

    dcc.DatePickerSingle(id='demo_picker',
                         date=date(2023, 10, 31),
                         max_date_allowed=datetime.now().date(),
                         min_date_allowed=date(1920, 1, 1),
                         placeholder="select date to see records"),

    dcc.Interval(id='interval', interval=1000 * 1),

    html.H2(children='Wind Direction Historic', style={'textAlign': 'left'}),
    dcc.Graph(id='wind_dir_fig'),

    html.H2(children='Wind Speed (km/H)', style={'textAlign': 'left'}),
    dcc.Graph(id='wind_spd_fig'),

    html.H2(children='Rainfall Totals', style={'textAlign': 'left'}),
    dcc.Graph(id='rainfall_fig'),

    html.H2(children='Temperature(degrees Celsius)', style={'textAlign': 'left'}),
    dcc.Graph(id='temp_fig'),

    html.H2(children='Atmospheric Pressure (mPascals)', style={'textAlign': 'left'}),
    dcc.Graph(id='pressure_fig'),

    html.H2(children='Relative Humidity', style={'textAlign': 'left'}),
    dcc.Graph(id='humidity_fig'),
])


@callback(
    Output('wind_dir_fig', 'figure'),
    Output('wind_spd_fig', 'figure'),
    Output('rainfall_fig', 'figure'),
    Output('temp_fig', 'figure'),
    Output('pressure_fig', 'figure'),
    Output('humidity_fig', 'figure'),
    Input('interval', 'n_intervals'),
    # Input('demo_picker', 'value'),
)
def update_from_database(interval, demo_picker):
    df = get_queried_df()
    wind_data = munge_wind_data(df)

    wind_dir_fig = create_wind_polar_plot(wind_data)

    wind_spd_fig = create_wind_speed_plot(df)

    rainfall_fig = create_rainfall_plot(df)

    temp_fig = create_temp_plot(df)

    pressure_fig = create_pressure_plot(df)

    humidity_fig = create_humidity_plot(df)

    return wind_dir_fig, wind_spd_fig, rainfall_fig,temp_fig, pressure_fig, humidity_fig


def main():
    app.run(host='0.0.0.0')
    print("ran app")
