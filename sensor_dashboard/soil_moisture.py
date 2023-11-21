from flask import app
from plotly import graph_objects as go
from py import test
from sensor_dashboard.connection import get_queried_df
from dash import Dash, html, dcc, Output, Input, callback

def create_sm_plot(df):
    sm_df = df[df['measurement'] == 'soil_moisture']
    fig = go.Figure(data=go.Scatter(x=df['time'], y=df['value']))
    return fig


app = Dash(__name__)
app.layout = html.Div([
    html.H1(id='soil_moisture',
            children='Soil Moisture Data',
            style={'textAlign': 'center'}),
    dcc.Interval(id='interval', interval=1000 * 1),

    html.H2(children='Soil Moisture', style={'textAlign': 'left'}),
    dcc.Graph(id='sm_fig'),
])

@callback(
    Output('sm_fig', 'figure'),
    Input('interval', 'n_intervals'),
)
def update_from_database(interval):
    df = get_queried_df()
    sm_fig = create_sm_plot(df)
    return sm_fig

def run_soil_moisture():
    app.run(host='0.0.0.0')