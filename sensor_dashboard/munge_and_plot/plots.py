import pandas as pd
from dash import dcc
from dash.exceptions import PreventUpdate
import plotly.express as px
from plotly import graph_objects as go
from icecream import ic


class MeasurementPlot:
    def __init__(self, target_measurement, units, measurement_range,
                 title=None) -> None:
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

    def update_df(self, data) -> None:
        ic()
        df = pd.DataFrame(data)
        self.target_df = df[df['measurement'] == self.target_measurement]
