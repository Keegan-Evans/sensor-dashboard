import sqlite3
import pandas as pd

cnx = sqlite3.connect("./data/sensor_data.db")
# cur = con.cursor()

# res = cur.execute("SELECT * FROM air_quality")

aq_df = pd.read_sql_query("SELECT * FROM air_quality", cnx)

print(aq_df['timestamp'].head())

aq_df['timestamp'] = pd.to_datetime(list(map(lambda x: int(x * 10**9), aq_df['timestamp'])))
print(aq_df['timestamp'].head())

print("-" * 80)

# dash setup stuff
import dash
from dash import Dash, html, dcc, callback, Output, Input, dash_table
import plotly.express as px

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div(children='show data'),
    dash_table.DataTable(data=aq_df.to_dict('records'), page_size=10),
    dcc.Graph(figure=px.scatter(aq_df, x='timestamp', y='co2')),
    dcc.Graph(figure=px.scatter(aq_df, x='timestamp', y='ethanol')),
])

if __name__ == '__main__':
    app.run()