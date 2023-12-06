from dash import Dash, html, dcc, Output, Input, State
from dash.exceptions import PreventUpdate
from sensor_dashboard.connection import get_queried_df, testing_fp, default_fp
from sensor_dashboard.munge_and_plot import (
    munge_wind_data, create_wind_polar_plot, update_wind_polar_layout
    )
from sensor_dashboard.munge_and_plot.plots import MeasurementPlot
from icecream import ic
import datetime as dt
import pandas as pd
# import logging
import sensor_dashboard.util as util

# disable logging to stderr
# logging.getLogger().disabled = True
# logging.basicConfig(level=logging.WARNING)

app = Dash(__name__)


###################
# data management callbacks
# TODO: add error messaging for returning date range with no data.


# callback to get data from database
@app.callback(
    Output('all_data', 'data'),
    Output('data-retrieval-status', 'children'),
    [Input('interval', 'n_intervals'),
     State('selected_dates', 'data')])
def get_data(interval, selected_dates):
    ic()
    if selected_dates == []:
        ic("Dates not yet selected")
        raise PreventUpdate
    dates = [dt.date.fromtimestamp(x).strftime("%m-%d-%Y")
             for x in selected_dates]
    ic(
        interval,
        dates
       )

    fp = default_fp
    # fp = testing_fp_fp

    try:
        df = get_queried_df(fp,
                            start_date=selected_dates[0],
                            end_date=selected_dates[1])

    except Exception as e:
        ic(str(e))
        raise PreventUpdate
        
    return_data = df.to_dict('records')
    return return_data, "Data last retrieved: {}".format(dt.datetime.now())


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
    ic()
    dff = pd.DataFrame(data)
    most_recent = str(dff['time'].max())
    return f"Last sensor data reading: {most_recent}"


# create data for wind polar
@app.callback(
    Output('wind_data', 'data'),
    [Input('all_data', 'data')],
)
def get_wind_data(data):
    ic()
    dff = pd.DataFrame(data)
    wind_data = munge_wind_data(dff).to_dict('records')
    ic('wind data created, adding to wind_data store')

    return wind_data


###################
# plot callbacks
# wind polar plot
@app.callback(
    Output('wind_polar', 'children'),
    [Input('wind_data', 'data'),],
)
def create_polar_plot(data):
    ic()
    if not data:
        ic("data not yet available for wind polar plot")
        raise PreventUpdate
    dff = pd.DataFrame(data)
    figure = create_wind_polar_plot(dff)
    update_wind_polar_layout(figure)
    return dcc.Graph(figure=figure)


###################
# standard measurement plots

humidity_plot = MeasurementPlot(
    target_measurement='humidity',
    units='%',
    measurement_range=[0, 100],
    input_name='all_data',
    output_name='humidity_plot',
    app=app,
    title='Humidity')

rainfall_plot = MeasurementPlot(
    target_measurement='rainfall',
    units='mm',
    measurement_range=[0, 250],
    input_name='all_data',
    output_name='rainfall_plot',
    app=app,
    title='Rainfall')

windspeed_plot = MeasurementPlot(
    target_measurement='wind_speed_beaufort',
    units='kph',
    measurement_range=[0, 75],
    input_name='all_data',
    output_name='windspeed_plot',
    app=app,
    title='Wind Speed')

temperature_plot = MeasurementPlot(
    target_measurement='temperature',
    units='°C',
    measurement_range=[-25, 35],
    input_name='all_data',
    output_name='temperature_plot',
    app=app,
    title='Temperature')


# Atmospheric pressure in hPa
# pressure_plot = MeasurementPlot('pressure', 'hPa', [0, 1100])
temperature_plot = MeasurementPlot(
    target_measurement='pressure',
    units='hPa',
    measurement_range=[0, 1100],
    input_name='all_data',
    output_name='pressure_plot',
    app=app,
    title='Atmospheric Pressure')


######################
# Data picking stuff

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
    html.Div(id='last-update'),

    dcc.Store(id='all_data', storage_type='memory', data=[]),
    html.Div(id='data-retrieval-status'),
    dcc.Store(id='wind_data', storage_type='memory', data=[]),
    dcc.Interval(id='interval', interval=1000 * 60),

    html.Div(id='wind_polar', children=[]),
    html.Div(id='windspeed_plot', children=[]),
    html.Div(id='temperature_plot', children=[]),
    html.Div(id='pressure_plot', children=[]),
    html.Div(id='humidity_plot', children=[]),
    html.Div(id='rainfall_plot', children=[]),
])


def main():
    ic.enable()
    ic("running app")
    app.run(host='0.0.0.0', debug=True)
    # app.run(host='0.0.0.0', debug=False)


if __name__ == "__main__":
    main()
