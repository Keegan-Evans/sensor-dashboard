from doctest import debug
from tabnanny import verbose
import uu
from dash import Dash, html, dcc, Output, Input, State, CeleryManager, no_update, ctx
from dash.exceptions import PreventUpdate
from sensor_dashboard.connection import get_queried_df, testing_fp, default_fp

from sensor_dashboard.munge_and_plot import (
    get_wind_df, WindRosePlot, MeasurementPlot
    )

from icecream import ic
import datetime as dt
import pandas as pd
from sensor_dashboard.util import get_default_dates
import sensor_dashboard.util as util
import os
# from uuid import uuid4

from flask_caching import Cache
from celery import Celery

ic.disable()


# TODO: Get rid of this when date picker is enabled
# launch_uid = uuid4()
default_dates = default_start, default_end = get_default_dates()


###################
# App and Cache setup
ic.enable()
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')
CACHE_CONFIG = {
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': REDIS_URL
}
celery_app = ic(Celery(__name__, broker=REDIS_URL, backend=REDIS_URL))
celery_background = ic(CeleryManager(celery_app,
                                    #  cache_by=[lambda: launch_uid]
                                     ))
dash_app = ic(Dash(background_callback_manager=celery_background))
dash_app = Dash()
dash_server = ic(dash_app.server)


cache = ic(Cache())
assert isinstance(cache, Cache)

ic(cache.init_app(dash_server, CACHE_CONFIG))

###################
# cached data functions
# TODO: Set these up as callbacks on long interval to refresh data.

@cache.memoize()
def cache_data():
    ic()
    df = ic(get_queried_df(db_fp=testing_fp,
                           start_date=default_start,
                           end_date=default_end,
                           ))
    return df


ic(cache_data())


def get_cached_data(measurement):
    df = cache_data()
    df = df[df['measurement'] == measurement]
    return df


@cache.memoize()
def cache_wind_data():
    ic()
    df = ic(get_wind_df(db_fp=testing_fp,
                        start_date=default_start,
                        end_date=default_end,
                        ))
    return df

ic(cache_wind_data())


###################
# data management callbacks
@dash_app.callback(
    Output('signal', 'data'),
    Input('interval', 'n_intervals'),
    # background_callback_manager=celery_background,
)
def populate_cache(interval):
    ic()
    ic(cache_data())
    ic("global data cached")

@dash_app.callback(
    Output('wind-signal', 'data'),
    [Input('signal', 'data')],
    # prevent_initial_call=True,
    # background=True,
    # background_callback_manager=celery_background,
)
def populate_wind_cache(signal):
    ic()
    ic(cache_wind_data())
    ic("wind data cached")




# TODO: add error messaging for returning date range with no data.
# callback to get data from database
# @dash_app.callback(
#     output=[
#         Output('all_data', 'data'),
#         Output('data-retrieval-status', 'children'),
#     ],
#     inputs=[
#         Input('interval', 'n_intervals'),
#         State('selected_dates', 'data')
#         ],
#     # background=True,
#     # manager=background_callback_manager)
#     )
# def get_data(interval, selected_dates):
#     ic()
#     if selected_dates == []:
#         ic("Dates not yet selected")
#         selected_dates = default_dates
#     dates = [dt.date.fromtimestamp(x).strftime("%m-%d-%Y")
#              for x in selected_dates]
#     ic(
#         interval,
#         dates
#        )
# # 
#     fp = default_fp
#     # fp = testing_fp

    # try:
        # df = get_queried_df(fp,
                            # start_date=selected_dates[0],
                            # end_date=selected_dates[1])
        # ic(df.head())
# 
    # except Exception as e:
        # ic(str(e))
        # ic("unable to retrieve from db")
        # return no_update, "Data retrieval failed at: {} with {}".format(dt.datetime.now(), e)
        # 
    # return_data = df.to_dict('records')
    # return return_data, "Data last retrieved: {}".format(dt.datetime.now())


# @dash_app.callback(
#     Output('output-container-range-slider', 'children'),
#     Output('selected_dates', 'data'),
#     [Input('date-picker', 'value'),
#      Input('interval', 'n_intervals')
#     ])
# def update_selected_dates(value, interval):
#     ic()
#     ic(value)
#     return (
#         'Select date range of data to view with slider.\n'
#         ' Currently selected range: {} to {}'.format(
#             dt.date.fromtimestamp(value[0]).strftime("%m-%d-%Y"),
#             dt.date.fromtimestamp(value[1]).strftime("%m-%d-%Y")),
#         value
#         )


# get timestamp of last update
# @dash_app.callback(
    # Output('last-update', 'children'),
    # [Input('all_data', 'data')],
# )
# def show_last_update(data):
    # ic()
    # dff = pd.DataFrame(data)
    # most_recent = str(dff['time'].max())
    # return f"Last sensor data reading: {most_recent}"

# create data for wind polar
# @dash_app.callback(
    # Output('wind_data', 'data'),
    # [Input('all_data', 'data')],
# )
# def create_wind_data(data):
    # ic()
    # dff = pd.DataFrame(data)
    # wind_data = munge_wind_data(dff).to_dict('records')
    # ic('wind data created, adding to wind_data store')
# 
    # return wind_data
###################
# plot callbacks
# wind polar plot
polar_plot = WindRosePlot(input_name='wind-signal',
                          output_name='wind_polar',
                          app=dash_app,
                          data_caller=cache_wind_data,
                          )


###################
# standard measurement plots
humidity_plot = MeasurementPlot(
    target_measurement='humidity',
    units='%',
    measurement_range=[0, 100],
    input_name='signal',
    output_name='humidity_plot',
    app=dash_app,
    title='Humidity',
    data_caller=get_cached_data)

rainfall_plot = MeasurementPlot(
    target_measurement='rainfall',
    units='mm',
    measurement_range=[0, 250],
    input_name='signal',
    output_name='rainfall_plot',
    app=dash_app,
    title='Rainfall',
    data_caller=get_cached_data)

windspeed_plot = MeasurementPlot(
    target_measurement='wind_speed_beaufort',
    units='kph',
    measurement_range=[0, 75],
    input_name='signal',
    output_name='windspeed_plot',
    app=dash_app,
    title='Wind Speed',
    data_caller=get_cached_data)

temperature_plot = MeasurementPlot(
    target_measurement='temperature',
    units='°C',
    measurement_range=[-25, 35],
    input_name='signal',
    output_name='temperature_plot',
    app=dash_app,
    title='Temperature',
    data_caller=get_cached_data)


# Atmospheric pressure in hPa
# pressure_plot = MeasurementPlot('pressure', 'hPa', [0, 1100])
pressure_plot = MeasurementPlot(
    target_measurement='pressure',
    units='hPa',
    measurement_range=[0, 1100],
    input_name='signal',
    output_name='pressure_plot',
    app=dash_app,
    title='Atmospheric Pressure',
    data_caller=get_cached_data)


######################
# Data picking stuff


# range_slider = dcc.RangeSlider(
#     id='date-picker',
#     value=[default_start, default_end],
#     step=util.day_seconds,
#     min=default_start,
#     max=default_end,
#     marks=None
# )

dash_app.layout = html.Div([

    html.H1(id='weather_station',
            children='Weather Station Data',
            style={'textAlign': 'center'}),
    # range_slider,
    # dcc.Store(id='selected_dates', storage_type='memory', data=[]),
    # html.Button('Update Data', id='get-data'),

    # html.Div(id='output-container-range-slider'),
    # html.Div(id='last-update'),

    # dcc.Store(id='all_data', storage_type='memory', data=[]),
    # html.Div(id='data-retrieval-status'),
    # dcc.Store(id='wind_data', storage_type='memory', data=[]),
    dcc.Interval(id='interval', interval=1000 * 60 * 5),
    # html.Div(id='getting-data', children=[])


    html.Div(id='wind_polar', children=[]),
    html.Div(id='windspeed_plot', children=[]),
    html.Div(id='temperature_plot', children=[]),
    html.Div(id='pressure_plot', children=[]),
    html.Div(id='humidity_plot', children=[]),
    html.Div(id='rainfall_plot', children=[]),

    dcc.Store('signal'),
    dcc.Store('wind-signal')
])
ic("end bookmark")



if __name__ == "__main__":
    ic.enable()
    dash_app.run('0.0.0.0', debug=True)
