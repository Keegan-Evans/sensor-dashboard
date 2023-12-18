import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def just_wind_data(df: pd.DataFrame):
    binned_speed_df = df[df['measurement'] == 'wind_speed_beaufort']
    binned_wind_dir_df = df[df['measurement'] == 'cardinal_direction']

    binned_wind = binned_speed_df.merge(binned_wind_dir_df, on='time', suffixes=('_speed', '_dir'))

    return binned_wind

    
def munge_wind_data(df: pd.DataFrame):
    # get only beaufort and cardinal direction
    wind = just_wind_data(df)
    wind_w_freq = generate_frequency_by_cardinal_and_strength(wind) 

    return wind_w_freq


def generate_frequency_by_cardinal_and_strength(
        df,
        cardinal_dir_col='str_value_dir',
        beaufort_col='str_value_speed'):

    comb_wind = df.groupby(cardinal_dir_col).value_counts(subset=[beaufort_col], normalize=True,)
    comb_wind.name = 'proportion_frequency_by_cardinal_and_strength'

    out_df = df.merge(comb_wind, left_on=[cardinal_dir_col, beaufort_col],
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


def add_trace_by_beaufort(fig, beaufort, df):
    fig.add_trace(go.Barpolar(
        r=df['proportion_frequency_by_cardinal_and_strength'].where(
            df['beaufort'] == beaufort),
        theta=df['cardinal_midpoints'].where(
            df['beaufort'] == beaufort),
        name=beaufort,
        width=(360/16),
        marker_color=beaufort_colors[beaufort_labels.index(beaufort)]
    ))


def update_trace_by_beaufort(fig, beaufort, df):
    fig.update_traces(
        r=df['proportion_frequency_by_cardinal_and_strength'].where(
            df['beaufort'] == beaufort),
        theta=df['cardinal_midpoints'].where(
            df['beaufort'] == beaufort),
        name=beaufort,
        width=(360/16),
        marker_color=beaufort_colors[beaufort_labels.index(beaufort)]
    )


def create_wind_polar_plot(df):
    fig = go.Figure()

    for label in beaufort_labels:
        add_trace_by_beaufort(fig, label, df)

    fig.update_layout(
        polar=dict(
            angularaxis=dict(showticklabels=True, ticks='outside',
                             type='linear', rotation=90,
                             direction='clockwise',
                             tickvals=[0, 45, 90, 135, 180, 225, 270, 315],
                             ticktext=['N', 'NE', 'E', 'SE', 'S', 'SW', 'W',
                                       'NW']
                             )
        )
    )

    return fig


def update_wind_polar_plot(fig, df):
    for label in beaufort_labels:
        update_trace_by_beaufort(fig, label, df)
    # return fig


def create_wind_speed_plot(df):
    wind_spd_df = df[df.measurement == 'wind_speed_beaufort']
    fig = go.Figure()
    fig.add_scatter(x=wind_spd_df['time'], y=wind_spd_df['value'])
    # fig = px.scatter(wind_spd_df, x='time', y='value')
    return fig


def create_rainfall_plot(df):
    rainfall_df = df[df.measurement == 'rainfall']
    fig = go.Figure()
    fig.add_trace(
        go.Histogram(
            x=rainfall_df['time'],
            y=rainfall_df['value'],
            histfunc='sum',
            autobinx=True,))
    fig.update_layout(bargap=0.2)
    return fig

    