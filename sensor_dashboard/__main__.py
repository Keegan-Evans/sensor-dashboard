from dash import Dash, html, dcc, Output, Input, State
from dash.exceptions import PreventUpdate
from sensor_dashboard.connection import get_queried_df
from sensor_dashboard.munge_and_plot import (
    munge_wind_data, create_wind_polar_plot, update_wind_polar_layout
    )
from sensor_dashboard.munge_and_plot.plots import MeasurementPlot
import icecream as ic
import datetime as dt
import pandas as pd
import logging
import sensor_dashboard.util as util

# disable logging to stderr
# logging.getLogger().disabled = True
logging.basicConfig(level=logging.WARNING)

app = Dash(__name__)
###################
# data management callbacks
# TODO: add error messaging for returning date range with no data.


# callback to get data from database
@app.callback(
    Output('all_data', 'data'),
    [Input('interval', 'n_intervals'),
     Input('selected_dates', 'data')])
def get_data(interval, selected_dates):
    ic.ic(selected_dates)
    try:
        df = get_queried_df(start_date=selected_dates[0],
                            end_date=selected_dates[1])
        return_data = df.to_dict('records')
        ic.ic(return_data)
        return return_data

    except ValueError:
        raise PreventUpdate


@app.callback(
    Output('output-container-range-slider', 'children'),
    Output('selected_dates', 'data'),
    Input('date-picker', 'value'))
def update_output(value):
    return (
        'Select date range of data to view with slider.\n'
        ' Currently selected range: {} to {}'.format(
            dt.date.fromtimestamp(value[0]).strftime("%m-%d-%Y"),
            dt.date.fromtimestamp(value[1]).strftime("%m-%d-%Y")),
        value
        )


# get timestamp of last update
@app.callback(
    Output('last-update', 'children'),
    [Input('all_data', 'data')],
)
def show_last_update(data):
    if not data:
        raise PreventUpdate
    dff = pd.DataFrame(data)
    most_recent = str(dff['time'].max())
    return f"Last sensor data reading: {most_recent}"


# create data for wind polar
@app.callback(
    Output('wind_data', 'data'),
    [Input('all_data', 'data')],
)
def get_wind_data(data):
    dff = pd.DataFrame(data)
    wind_data = munge_wind_data(dff).to_dict('records')

    return wind_data


###################
# plot callbacks
# wind polar plot
@app.callback(
    Output('wind_polar', 'children'),
    [Input('interval', 'n_intervals'),
     State('wind_data', 'data')],
)
def create_polar_plot(interval, data):
    if not data:
        raise PreventUpdate
    dff = pd.DataFrame(data)
    figure = create_wind_polar_plot(dff)
    update_wind_polar_layout(figure)
    return dcc.Graph(figure=figure)


humidity_plot = MeasurementPlot('humidity', '%', [0, 100])


@app.callback(
    Output('humidity_plot', 'children'),
    [Input('all_data', 'data')],
)
def draw_humidity_plot(data):
    humidity_plot.update_df(data)
    return humidity_plot.graph


rainfall_plot = MeasurementPlot('rainfall', 'mm', [0, 55])


@app.callback(
    Output('rainfall_plot', 'children'),
    [Input('all_data', 'data')],
)
def draw_plot(data):
    rainfall_plot.update_df(data)
    return rainfall_plot.graph


windspeed_plot = MeasurementPlot(
    'wind_speed_beaufort', '%', [0, 100], title='Wind Speed')


@app.callback(
    Output('windspeed_plot', 'children'),
    [Input('all_data', 'data')],
)
def draw_windspeed_plot(data):
    windspeed_plot.update_df(data)
    return windspeed_plot.graph


temperature_plot = MeasurementPlot('temperature', '°C', [-25, 35])


@app.callback(
    Output('temperature_plot', 'children'),
    [Input('all_data', 'data')],
)
def draw_temperature_plot(data):
    temperature_plot.update_df(data)
    return temperature_plot.graph


# Atmospheric pressure in hPa
pressure_plot = MeasurementPlot('pressure', 'hPa', [0, 1100])


@app.callback(
    Output('pressure_plot', 'children'),
    [Input('all_data', 'data')],
)
def draw_pressure_plot(data):
    pressure_plot.update_df(data)
    return pressure_plot.graph


default_start, default_end = util.get_default_times()

range_slider = dcc.RangeSlider(
    id='date-picker',
    value=[default_start, default_end],
    step=util.day_seconds,
    min=default_start,
    max=default_end,
    marks=None
)


app.layout = html.Div([

    html.H1(id='weather_station',
            children='Weather Station Data',
            style={'textAlign': 'center'}),
    range_slider,
    dcc.Store(id='selected_dates', storage_type='memory', data=[]),

    html.Div(id='output-container-range-slider'),

    dcc.Store(id='all_data', storage_type='memory', data=[]),
    dcc.Store(id='wind_data', storage_type='memory', data=[]),
    dcc.Interval(id='interval', interval=1000 * 15),

    html.Div(id='wind_polar', children=[]),
    html.Div(id='windspeed_plot', children=[]),
    html.Div(id='temperature_plot', children=[]),
    html.Div(id='pressure_plot', children=[]),
    html.Div(id='humidity_plot', children=[]),
    html.Div(id='rainfall_plot', children=[]),
    html.Div(id='last-update'),
])


def main():
    ic.ic.disable()
    app.run(host='0.0.0.0', debug=True)
    # app.run(host='0.0.0.0', debug=False)
    print("ran app")


if __name__ == "__main__":
    main()
