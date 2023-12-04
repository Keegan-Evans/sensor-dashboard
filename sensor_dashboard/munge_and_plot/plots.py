from cProfile import label
import pandas as pd
from dash import dcc
from dash.exceptions import PreventUpdate
from plotly import graph_objects as go
from pytest import mark


class MeasurementPlot:
    def __init__(self, target_measurement, units, measurement_range,
                 title=None) -> None:
        self.target_measurement = target_measurement
        self.units = units
        if title:
            self.title = title
        else:
            self.title = self.target_measurement.capitalize()
        self.measurement_range = measurement_range
        self._fig = go.Figure()
        self.target_df = None

    @property
    def graph(self) -> dcc.Graph:
        self.draw_trace()
        self.update_layout()
        return dcc.Graph(figure=self._fig)

    def draw_trace(self) -> None:
        if self.target_df is None:
            raise PreventUpdate

        if self.target_df['measurement'] is None:
            raise PreventUpdate

        trace = go.Scatter(
            x=self.target_df['time'],
            y=self.target_df['value'],
            mode='markers',
        )
        self._fig.update_traces(trace)

    def update_layout(self) -> None:
        layout = go.Layout(
            title=self.title,
            xaxis=dict(
                title='Time',
                titlefont_size=16,
                tickfont_size=14,
                marker=dict(
                    color='rgb(0, 0, 0)',

                ),  
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
        if data is None:
            raise PreventUpdate

        df = pd.DataFrame(data)
        self.target_df = df[df.measurement == self.target_measurement]

