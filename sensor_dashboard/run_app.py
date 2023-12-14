from icecream import ic
from sensor_dashboard.weather_station_app import dash_app

ic.enable()
server = dash_app.server

if __name__ == "__main__":
    ic.enable()
    dash_app.run_server(debug=True)