import pandas as pd
import plotly.express as px


def create_temp_plot(df: pd.DataFrame):
    temp_df = df[df['measurement'] == 'temperature']

    fig = px.scatter(temp_df, x='time', y='value', title='Temperature')
    return fig


def create_pressure_plot(df: pd.DataFrame):
    pressure_df = df[df['measurement'] == 'pressure']

    fig = px.scatter(pressure_df, x='time', y='value', title='Atmospheric Pressure')
    return fig

def create_humidity_plot(df: pd.DataFrame):
    humidity_df = df[df['measurement'] == 'humidity']

    fig = px.scatter(humidity_df, x='time', y='value', title='Relative Humidity')
    return fig