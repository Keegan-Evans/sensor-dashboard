from dash import Dash, html, dcc, State, Input, Output
import sqlite3
import os

update_frequeny = 1000 * 1  # 1 seconds
database_fp = os.path.join("sensor_dashboard", "tests", "data", "sensor_data.db")

app = Dash()

app.layout = html.Div([
    html.H1(id='yep'),
    dcc.Interval(id='interval', interval=update_frequeny),
])

@app.callback(
    Output('yep', 'children'),
    [Input('interval', 'n_intervals')]
)
def update(intervals):
    connection = sqlite3.connect(database_fp)
    cursor = connection.cursor()

    data = cursor.execute(
        "SELECT * FROM sensor_measurements ORDER BY time DESC"
    ).fetchone()
    print(data)
    return 993


if __name__ == '__main__':
    app.run_server(debug=True)