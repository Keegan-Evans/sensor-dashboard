from icecream import ic
from sensor_dashboard.weather_station_app import dash_app


def main():
    ic.enable()
    dash_app.run_server('0.0.0.0', debug=True)