from icecream import ic
import datetime as dt
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sensor_dashboard.connection import testing_fp
from mqtt_data_logger.sensor_data_models import SensorMeasurement, Measurement
from dash import Output, Input, dcc
from dash.exceptions import PreventUpdate
from sqlalchemy import create_engine, select, or_
from sqlalchemy.orm import joinedload
from sensor_dashboard.util import get_default_dates, limit_observations
import plotly.express as px


def get_wind_df(db_fp, start_date, end_date, drop_zeros=True):
    ic()

    dt_start_date = dt.datetime.fromtimestamp(start_date)
    dt_end_date = dt.datetime.fromtimestamp(end_date)

    sqlite_engine = create_engine(f"sqlite:///{db_fp}")

    query = select(SensorMeasurement)\
        .join(Measurement, onclause=SensorMeasurement.measurement)\
        .options(joinedload(SensorMeasurement.topic),
                 joinedload(SensorMeasurement.sensor),
                 joinedload(SensorMeasurement.
                            measurement))\
        .order_by(SensorMeasurement.time.asc())
    
    if drop_zeros:
        query = query.where(SensorMeasurement.value > 0)

    if dt_start_date:
        if not isinstance(dt_start_date, dt.date):
            raise ValueError("Provided value({}) for `start_date` is type {}, not datetime.date.".format(start_date, type(start_date)))
        query = query.where(SensorMeasurement.time >= dt_start_date)

    if dt_end_date:
        if not isinstance(dt_end_date, dt.date):
            raise ValueError("Provided value({}) for `end_date` is type {}, not datetime.date.".format(end_date, type(end_date)))
        query = query.where(SensorMeasurement.time <= dt_end_date)
    
    # get only binned wind data
    query = query.where(or_(Measurement.measurement == 'cardinal_direction',
                            Measurement.measurement == 'wind_speed_beaufort'))

    with sqlite_engine.connect() as connection:
        raw_wind_df = pd.read_sql(query, connection)
        ic(raw_wind_df.shape)
        ic(raw_wind_df.head())

    # now combine into single dataframe
    final_wind_df = ic(munge_wind_data(raw_wind_df))
    ic(final_wind_df.shape)
    ic(final_wind_df.head())
    return final_wind_df


def just_wind_data(df: pd.DataFrame):
    df['measurement'].unique()
    binned_speed_df = df[df['measurement'] == 'wind_speed_beaufort'].copy()
    binned_wind_dir_df = df[df['measurement'] == 'cardinal_direction'].copy()

    binned_wind = binned_speed_df.merge(
        binned_wind_dir_df,
        on='time',
        suffixes=('_speed', '_dir')
        )

    return binned_wind

    
def munge_wind_data(df: pd.DataFrame):
    # get only beaufort and cardinal direction
    wind = just_wind_data(df)
    wind_w_freq = generate_frequency_by_cardinal_and_strength(wind) 
    return_wind_df = limit_observations(wind_w_freq, 150)

    return return_wind_df


def generate_frequency_by_cardinal_and_strength(
        df,
        cardinal_dir_col='str_value_dir',
        beaufort_col='str_value_speed'):

    comb_wind = df.groupby(cardinal_dir_col).value_counts(
        subset=[beaufort_col],
        normalize=True,
        )
    comb_wind.name = 'proportion_frequency_by_cardinal_and_strength'

    out_df = df.merge(comb_wind,
                      left_on=[cardinal_dir_col, beaufort_col],
                      right_on=[cardinal_dir_col, beaufort_col])
    out_df.rename(columns={beaufort_col: 'beaufort',
                           cardinal_dir_col: 'cardinal_direction',
                           'value_dir': 'cardinal_midpoints'},
                  inplace=True)
    return out_df


beaufort_labels = ['Calm', 'Light Air', 'Light Breeze',
                   'Gentle Breeze', 'Moderate Breeze', 'Fresh Breeze',
                   'Strong Breeze', 'Near Gale', 'Gale', 'Strong Gale',
                   'Storm', 'Violent Storm', 'Hurricane Force']

beaufort_colors = [
    "#f7f7f7", "#f0f921", "#ebd634", "#d1cf32", "#a1d059",
    "#6fc060", "#2a9d8f", "#007f5f", "#006050", "#004b7d",
    "#00326d", "#001b52", "#000028"
]
beaufort_order_map = {
    'Calm': 0,
    'Light Air': 1,
    'Light Breeze': 2,
    'Gentle Breeze': 3,
    'Moderate Breeze': 4,
    'Fresh Breeze': 5,
    'Strong Breeze': 6,
    'Near Gale': 7,
    'Gale': 8,
    'Strong Gale': 9,
    'Storm': 10,
    'Violent Storm': 11,
    'Hurricane Force': 12
    }

beaufort_color_map = {
    'Calm': '#f7f7f7',
    'Light Air': '#f0f921',
    'Light Breeze': '#ebd634',
    'Gentle Breeze': '#d1cf32',
    'Moderate Breeze': '#a1d059',
    'Fresh Breeze': '#6fc060',
    'Strong Breeze': '#2a9d8f',
    'Near Gale': '#007f5f',
    'Gale': '#006050',
    'Strong Gale': '#004b7d',
    'Storm': '#00326d',
    'Violent Storm': '#001b52',
    'Hurricane Force': '#000028'
    }



# def add_trace_by_beaufort(fig, beaufort, df):
#     fig.add_trace(go.Barpolar(
#         r=df['proportion_frequency_by_cardinal_and_strength'].where(
#             df['beaufort'] == beaufort),
#         theta=df['cardinal_midpoints'].where(
#             df['beaufort'] == beaufort),
#         customdata=df[['cardinal_direction', 'beaufort']],
#         name=beaufort,
#         width=(360/16),
#         marker_color=beaufort_colors[beaufort_labels.index(beaufort)],
#         hovertemplate='<br>'.join([
#             'Direction: %{customdata[0]}',
#             'Beaufort: %{customdata[1]}'
#         ]),
#     ))


# def update_wind_polar_layout(fig):
    # layout = go.Layout(
        # title='Wind Distribution',
        # polar=dict(
            # 
            # angularaxis=dict(
                # showticklabels=True,
                # ticks='outside',
                # type='linear',
                # rotation=90,
                # direction='clockwise',
                # tickvals=[0, 45, 90, 135, 180, 225, 270, 315],
                # ticktext=['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
            # ),
            # radialaxis=dict(
                # showticklabels=False),
        # )
    # )
    # fig.update_layout(layout)


# def create_wind_polar_plot(df):
#     fig = go.Figure()

#     for label in beaufort_labels:
#         add_trace_by_beaufort(fig, label, df)
    
#     # update_wind_polar_layout(fig)

#     return fig


# def update_wind_plot_layout(fig):
#     layout = go.Layout(
#         title='Wind Speed',
#         xaxis=dict(
#             title='Time',
#             titlefont_size=16,
#             tickfont_size=14,
#         ),
#         yaxis=dict(
#             title='km/h',
#             titlefont_size=16,
#             tickfont_size=14,
#             range=[0, 80],
#         ),
#         legend=dict(
#             x=0,
#             y=1.0,
#             bgcolor='rgba(255, 255, 255, 0)',
#             bordercolor='rgba(255, 255, 255, 0)'
#         ),
#     )
#     fig.update_layout(layout)


def split_into_chunks_of_size_k(x, k):
    split = [np.array(x)[i:i + k] for i in
             range(0, len(x), k)]
    return split


def split_into_n_chunks(x, n):
    leftover = len(x) % n
    size = len(x) // n
    last = x.pop(-1)
    chunked = split_into_chunks_of_size_k(x, k=size)

    # ensure that spacing is not too close at end
    if leftover < 0.7 * size:
        chunked.pop(-1)

    splits = [each[0] for each in chunked]
    splits.append(last)
    return splits


class WindRosePlot:
    def __init__(self, input_name, output_name,
                 app, data_caller):
        self.app = app
        self.target_df = None
        self.data_caller = data_caller
        self._fig = None

        self.app.callback(
            Output(output_name, 'children'),
            [Input(input_name, 'data')],
            prevent_initial_call=True
        )(self.draw_plot)

    @property
    def figure(self):
        ic()
        if self._fig == None:
            ic("drawing figure")
            self._fig = px.bar_polar(
                self.target_df,
                r='proportion_frequency_by_cardinal_and_strength',
                # r='beaufort',
                theta='cardinal_midpoints',
                color='beaufort',
                # category_orders=beaufort_order_map,
                category_orders={'beaufort': beaufort_labels},
                color_discrete_map=beaufort_color_map,
                width=(360/16),
            )
            # self._fig.show()
        self.update_layout()
        
        
        # for label in beaufort_labels:
        #     try:
        #         ic(add_trace_by_beaufort(self._fig, label, self.target_df))
        #     except:
        #         ic(f"did not add trace for{label}")

        return dcc.Graph(figure=self._fig)
            
        
        
        # ic(self.target_df.head())
        # figure = ic(create_wind_polar_plot(self.target_df))
        # update_wind_polar_layout(figure)
        return dcc.Graph(figure=figure)

    def update_layout(self):
        ic()
        if self._fig is None:
            ic("tried to update figure layout when figure does not yet exist")
            raise PreventUpdate

        layout = go.Layout(
            title='Wind Distribution',
            polar=dict(

                angularaxis=dict(
                    showticklabels=True,
                    ticks='outside',
                    type='linear',
                    rotation=90,
                    direction='clockwise',
                    tickvals=[0, 45, 90, 135, 180, 225, 270, 315],
                    ticktext=['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
                ),
                radialaxis=dict(
                    showticklabels=False),
                
            )
        )

        self._fig.update_layout(layout)
        return None

    def update_df(self):
        ic()
        self.target_df = self.data_caller()

    def draw_plot(self, trigger):
        ic()
        self.update_df()
        return self.figure


if __name__ == '__main__':
    #####################
    # test wind df generation
    ic.enable()
    dates = get_default_dates()
    results = ic(get_wind_df(db_fp=testing_fp,
                             start_date=dates[0],
                             end_date=dates[1]))
    ic(results.columns)
    ######################

    # # for testing plotting
    from dash import dcc, Dash, html
    import os
    from flask_caching import Cache
# 
    ######################
    # App and Cache setup
    ic.enable()
    dash_app = ic(Dash())
    dash_server = ic(dash_app.server)
# 
    CACHE_CONFIG = {
        'CACHE_TYPE': 'redis',
        'CACHE_REDIS_URL': os.environ.get('REDIS_URL', 'redis://localhost:6379')
    }
# 
    cache = ic(Cache())
    assert isinstance(cache, Cache)
# 
    ic(cache.init_app(dash_server, CACHE_CONFIG))
# 
# 
    #################
    # cached data
# 
    default_dates = default_start, default_end = get_default_dates()
# 
    @cache.memoize()
    def cache_wind_data():
        ic()
        df = ic(get_wind_df(db_fp=testing_fp,
                            start_date=default_start,
                            end_date=default_end,
                            ))
        return df
# 
# 
    polar_plot = WindRosePlot(input_name='draw-wind',
                              output_name='polar-plot',
                              app=dash_app,
                              data_caller=cache_wind_data,
                              )
# 
    dash_app.layout = html.Div([
        html.Button('draw-wind', id='draw-wind'),
        html.Div(id='polar-plot', children=[]),
    ])
# 
    dash_app.run(debug=True)
# 
# 