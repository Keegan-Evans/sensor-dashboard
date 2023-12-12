from icecream import ic
from sensor_dashboard.weather_station_app import app

ic.enable()
server = app.server

if __name__ == "__main__":
    ic.enable()
    app.run_server(debug=True)