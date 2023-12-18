from numpy import empty
import pandas as pd
from sensor_dashboard.connection import get_queried_df, testing_fp
from sensor_dashboard.util import get_default_dates
from dash import dcc, Dash, Output, Input, html
from dash.exceptions import PreventUpdate
import plotly.express as px
from plotly import graph_objects as go
import os
from icecream import ic
from flask_caching import Cache


class MeasurementPlot:
    def __init__(self, target_measurement, units, measurement_range, app,
                 input_name, output_name, data_caller, title=None) -> None:
        ic()
        self.target_measurement = target_measurement
        self.units = units
        if title:
            self.title = title
        else:
            self.title = self.target_measurement.capitalize()
        self.measurement_range = measurement_range
        self._fig = None # go.Figure()
        self.target_df = None
        self.app = app
        self.data_caller = data_caller

        self.app.callback(
            Output(output_name, 'children'),
            [Input(input_name, 'data')],
            prevent_initial_call=True
        )(self.draw_plot)

    @property
    def layout(self) -> go.Layout:
        layout = go.Layout(
            title=self.title,
            xaxis=dict(
                title='Time',
                titlefont_size=16,
                tickfont_size=14,
                ),
            yaxis=dict(
                title=self.units,
                range=self.measurement_range,
            ),
            legend=dict(
                x=0,
                y=1.0,
                bgcolor='rgba(255, 255, 255, 0)',
                bordercolor='rgba(255, 255, 255, 0)'
            ),
        )
        return layout



    @property
    def figure(self) -> dcc.Graph:
        ic()
        if self._fig is None:
            self._fig = \
            px.scatter(self.target_df,
                       x='time',
                       y='value',
                       title=self.title,
                       labels={'x': 'Time', 'y': self.units},
                       range_y=self.measurement_range,
                       )
            ic("figure created for " + self.title)
            self._fig.update_layout(self.layout)
            ic("layout updated for " + self.title)

        return dcc.Graph(figure=self._fig)

    # def draw_trace(self) -> None:
        # ic()
        # trace = [go.Scatter(
            # x=self.target_df['time'],
            # y=self.target_df['value'],
            # mode='markers',
        # )]
        # ic(trace)
        # self._fig.data = trace
        # ic(self._fig)
        # self._fig.update_traces(trace)

    def update_layout(self) -> None:
        ic()
        layout = go.Layout(
            title=self.title,
            xaxis=dict(
                title='Time',
                titlefont_size=16,
                tickfont_size=14,
                ),
            yaxis=dict(
                title=self.units,
                range=self.measurement_range,
            ),
            legend=dict(
                x=0,
                y=1.0,
                bgcolor='rgba(255, 255, 255, 0)',
                bordercolor='rgba(255, 255, 255, 0)'
            ),
        )
        self._fig.update_layout(layout)

    def update_df(self) -> None:
        ic()
        self.target_df = self.data_caller(self.target_measurement)
        # self.target_df = get_queried_df(db_fp=testing_fp,
                            # start_date=self.dates[0],
                            # end_date=self.dates[1],
                            # target_measurement=self.target_measurement)

        # df = pd.DataFrame(data)

    # @app.callback(
        # Output('self.app.{}_plot'.format(self.title.lower()), 'children'),
        # [Input('self.app.all_data', 'data')
        #  ],
    # )
    def draw_plot(self, trigger):
        ic()
        self.update_df()
        if self.target_df is empty:
            raise PreventUpdate

        return self.figure


# if __name__ == '__main__':
#     # from sensor_dashboard.util import get_default_dates

#     # #######################
#     # # App and Cache setup
#     # ic.enable()
#     # dash_app = ic(Dash())
#     # dash_server = ic(dash_app.server)

#     # CACHE_CONFIG = {
#     #     'CACHE_TYPE': 'redis',
#     #     'CACHE_REDIS_URL': os.environ.get('REDIS_URL', 'redis://localhost:6379')
#     # }

#     # cache = ic(Cache())
#     # assert isinstance(cache, Cache)

#     # ic(cache.init_app(dash_server, CACHE_CONFIG))

#     # @cache.memoize()
#     # def cache_data():
#     #     ic()
#     #     df = ic(get_queried_df(db_fp=testing_fp,
#     #                            start_date=default_start,
#     #                            end_date=default_end,
#     #                            ))
#     #     return df
    
    
#     # def get_cached_data(measurement):
#     #     df = cache_data()
#     #     df = df[df['measurement'] == measurement]
#     #     return df

#     # default_start, default_end = get_default_dates()

#     # temperature_plot = MeasurementPlot(
#     #     target_measurement='temperature',
#     #     units='°C',
#     #     measurement_range=[-25, 35],
#     #     input_name='interval',
#     #     output_name='temperature_plot',
#     #     app=dash_app,
#     #     title='Temperature',
#     #     data_caller=get_cached_data)

#     # dash_app.layout = html.Div([
#     #     html.Div(id='temperature_plot', children=["Loading Temperature Data"]),
#     #     dcc.Interval(id='interval', interval=1000 * 25),
#     # ])

#     # dash_app.run(debug=True)