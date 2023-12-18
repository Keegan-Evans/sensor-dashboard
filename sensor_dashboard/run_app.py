from icecream import ic
from sensor_dashboard.weather_station_app import dash_app

ic.enable()

if __name__ == "__main__":
    ic.enable()

    dash_app.run_server(debug=True)