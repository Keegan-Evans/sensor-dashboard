from ast import Div
import pandas as pd
from sensor_dashboard.connection import get_queried_df, testing_fp
from dash import dcc, Dash, Output, Input
from dash.exceptions import PreventUpdate
import plotly.express as px
from plotly import graph_objects as go
from icecream import ic


class MeasurementPlot:
    def __init__(self, target_measurement, units, measurement_range,
                 input_name, output_name, dates, app: Dash, title=None) -> None:
        ic()
        self.target_measurement = target_measurement
        self.units = units
        if title:
            self.title = title
        else:
            self.title = self.target_measurement.capitalize()
        self.measurement_range = measurement_range
        self._fig = None # go.Figure()
        self.target_df = pd.DataFrame()
        self.dates = dates
        self.app = app

        self.app.callback(
            Output(output_name, 'children'),
            [Input(input_name, 'n_intervals')]
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
        self.target_df = get_queried_df(db_fp=testing_fp,
                            start_date=self.dates[0],
                            end_date=self.dates[1],
                            target_measurement=self.target_measurement)

        # df = pd.DataFrame(data)

    # @app.callback(
        # Output('self.app.{}_plot'.format(self.title.lower()), 'children'),
        # [Input('self.app.all_data', 'data')
        #  ],
    # )
    def draw_plot(self, trigger):
        ic()
        self.update_df()

        return self.figure

if __name__ == '__main__':
    from sensor_dashboard.util import get_default_dates
    from timeit import timeit
    from dash import Dash, html, dcc, DiskcacheManager
    ic.enable()

    default_dates = get_default_dates()
    import diskcache
    cache = diskcache.Cache("./cache")
    background_callback_manager = DiskcacheManager(cache)

    app = Dash(__name__, background_callback_manager=background_callback_manager)
    # app = Dash(__name__)



    temperature_plot = MeasurementPlot(
        target_measurement='temperature',
        units='°C',
        measurement_range=[-25, 35],
        input_name='interval',
        output_name='temperature_plot',
        dates=default_dates,
        app=app,
        title='Temperature')

    app.layout = html.Div([
        html.Div(id='temperature_plot', children=["Loading Temperature Data"]),
        dcc.Interval(id='interval', interval=1000 * 50),
    ])

    app.run('0.0.0.0', debug=True)
    # ic(temperature_plot.target_df)
    # ic(timeit(lambda: temperature_plot.update_df(), number=1))
    # ic(temperature_plot.target_df)