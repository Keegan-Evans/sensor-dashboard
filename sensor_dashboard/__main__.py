from sensor_dashboard.connection import get_queried_df
from  sensor_dashboard.munge_and_plot import (
    create_wind_polar_plot, munge_wind_data, create_wind_speed_plot,
    create_rainfall_plot,
)
from dash import Dash, html, dcc


# establish connection to database
# DONEE IN CONNECTION.PY

# LOOP

# read from database
# munge wind data for polar plot



# create and layout dash app
app = Dash(__name__)
app.layout = html.Div([

    html.H1(id='weather_station', children='Weather Station Data', style={'textAlign': 'center'}),
    dcc.Interval(id='interval', interval=1000 * 1),

    html.H2(children='Wind Direction Historic', style={'textAlign': 'left'}),
    dcc.Graph(id='wind_dir', figure=wind_dir_fig),

    html.H2(children='Wind Speed (km/H)', style={'textAlign': 'left'}),
    dcc.Graph(id='wind-speed-plot', figure=wind_spd_fig),

    html.H2(children='Rainfall Totals', style={'textAlign': 'left'}),
    dcc.Graph(id='rainfall', figure=rainfall_fig),
])

@app.callback(
    Output('weather_station', 'children'),
    [Input('interval', 'n_intervals')]
)
def update_from_database():
    df = get_queried_df()

    wind_data = munge_wind_data(df)

    # create polar plot for wind direction
    wind_dir_fig = create_wind_polar_plot(wind_data)
    wind_dir_fig.to_html('wind_dir_fig.html')

    # create scatter plot for wind speed
    wind_spd_fig = create_wind_speed_plot(df)
    wind_spd_fig.to_html('wind_spd_fig.html')

    # create scatter plot for rainfall
    rainfall_fig = create_rainfall_plot(df)
    rainfall_fig.to_html('rainfall_fig.html')   
    return [wind_dir_fig, wind_spd_fig, rainfall_fig]


def main():
    app.run(debug=True)
    print("ran app")

if __name__ == '__main__':
    main()


# Do I need to do a manual loop or does the dash app handle this for me?
# NEXT: embed the dash app in a flask app?
# wire app to 4CSCC website
