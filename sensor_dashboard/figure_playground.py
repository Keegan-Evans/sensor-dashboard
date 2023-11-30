from ast import In
from turtle import up
import pandas as pd
from sensor_dashboard.connection import get_queried_df
from sensor_dashboard.munge_and_plot import (
    create_wind_polar_plot, create_wind_speed_plot, update_wind_plot_layout
    )
from plotly import graph_objects as go
import plotly.express as px
from dash import Dash, html, dcc, Output, Input, State
import os
import icecream as ic
from dash.exceptions import PreventUpdate

from sensor_dashboard.munge_and_plot import (
    munge_wind_data,
)

testing_fp = os.path.join(".", "sensor_data.db")
ic.ic(testing_fp)
app = Dash(__name__)


# callback to get data from database
@app.callback(
    Output('all_data', 'data'),
    [Input('interval', 'n_intervals'),])
def get_data(interval):
    df = get_queried_df(testing_fp)
    return_data = df.to_dict('records')
    return return_data


# callback to munge wind data
@app.callback(
    Output('wind_data', 'data'),
    [Input('all_data', 'data')],
)
def get_wind_data(data):
    dff = pd.DataFrame(data)
    wind_data = munge_wind_data(dff).to_dict('records')

    return wind_data

# 
# @app.callback(
    # Output('demo_wind_fig', 'children'),
    # [Input('interval', 'n_intervals'),
    #  State('all_data', 'data')],
# )
# def draw_demo_fig(interval, data):
    # dff = pd.DataFrame(data)
    # if 'measurement' not in dff.columns:
        # raise PreventUpdate
    # dff = dff[dff['measurement'] == 'wind_speed_beaufort']
    # demo_fig = px.scatter(dff, x='time', y='value', color='str_value')
    # return dcc.Graph(figure=demo_fig)

@app.callback(
    Output('demo_wind_fig_2', 'children'),
    [Input('interval', 'n_intervals'),
     State('all_data', 'data')],
)
def draw_wind_fig(interval, data):
    dff = pd.DataFrame(data)
    if 'measurement' not in dff.columns:
        raise PreventUpdate
    figure = create_wind_speed_plot(dff, update_wind_plot_layout)
    update_wind_plot_layout(figure)
    return dcc.Graph(figure=figure)


@app.callback(
    Output('demo_polar_fig', 'children'),
    [Input('interval', 'n_intervals'),
     State('wind_data', 'data')],
)
def create_polar_plot(interval, data):
    if not data:
        raise PreventUpdate
    dff = pd.DataFrame(data)
    return dcc.Graph(figure=create_wind_polar_plot(dff))


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

app.layout = html.Div([
    dcc.Interval(id='interval', interval=1000 * 5),
    dcc.Store(id='default_layout', storage_type='memory', data=[]),
    dcc.Store(id='wind_data', storage_type='memory', data=[]),
    dcc.Store(id='all_data', storage_type='memory', data=[]),
    # html.Div(id='demo_wind_fig', children=[]),
    html.Div(id='demo_polar_fig', children=[]),
    html.Div(id='demo_wind_fig_2', children=[]),
    html.Div(id='last-update'),
])


if __name__ == '__main__':
    app.run(debug=True)