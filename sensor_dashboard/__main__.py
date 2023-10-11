from sensor_dashboard.connection import get_queried_df
from sensor_dashboard.munge_and_plot import (
    create_wind_polar_plot, munge_wind_data, create_wind_speed_plot,
    create_rainfall_plot,
)
from dash import Dash, html, dcc, Output, Input


app = Dash(__name__)
app.layout = html.Div([

    html.H1(id='weather_station',
            children='Weather Station Data',
            style={'textAlign': 'center'}),

    dcc.Interval(id='interval', interval=1000 * 1),

    html.H2(children='Wind Direction Historic', style={'textAlign': 'left'}),
    dcc.Graph(id='wind_dir'),

    html.H2(children='Wind Speed (km/H)', style={'textAlign': 'left'}),
    dcc.Graph(id='wind-speed-plot'),

    html.H2(children='Rainfall Totals', style={'textAlign': 'left'}),
    dcc.Graph(id='rainfall'),
])


@app.callback(
    Output('wind_dir', 'figure'),
    Output('wind-speed-plot', 'figure'),
    Output('rainfall', 'figure'),
    [Input('interval', 'n_intervals')]
)
def update_from_database(interval):
    df = get_queried_df()
    wind_data = munge_wind_data(df)

    wind_dir_fig = create_wind_polar_plot(wind_data)

    wind_spd_fig = create_wind_speed_plot(df)

    rainfall_fig = create_rainfall_plot(df)
    return wind_dir_fig, wind_spd_fig, rainfall_fig


def main():
    app.run(debug=True)
    print("ran app")


if __name__ == '__main__':
    main()


# Do I need to do a manual loop or does the dash app handle this for me?
# NEXT: embed the dash app in a flask app?
# wire app to 4CSCC website
