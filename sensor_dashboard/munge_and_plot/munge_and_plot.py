from icecream import ic
import pandas as pd
import numpy as np
import plotly.graph_objects as go


def just_wind_data(df: pd.DataFrame):
    ic(df['measurement'].unique())
    binned_speed_df = df[df['measurement'] == 'wind_speed_beaufort'].copy()
    binned_wind_dir_df = df[df['measurement'] == 'cardinal_direction'].copy()
    ic(binned_speed_df.head())
    ic(binned_wind_dir_df.head())

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

    return wind_w_freq


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


def add_trace_by_beaufort(fig, beaufort, df):
    fig.add_trace(go.Barpolar(
        r=df['proportion_frequency_by_cardinal_and_strength'].where(
            df['beaufort'] == beaufort),
        theta=df['cardinal_midpoints'].where(
            df['beaufort'] == beaufort),
        customdata=df[['cardinal_direction', 'beaufort']],
        name=beaufort,
        width=(360/16),
        marker_color=beaufort_colors[beaufort_labels.index(beaufort)],
        hovertemplate='<br>'.join([
            'Direction: %{customdata[0]}',
            'Beaufort: %{customdata[1]}'
        ]),
    ))


def update_wind_polar_layout(fig):
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
    fig.update_layout(layout)


def create_wind_polar_plot(df):
    fig = go.Figure()

    for label in beaufort_labels:
        add_trace_by_beaufort(fig, label, df)
    
    update_wind_plot_layout(fig)

    return fig


def update_wind_plot_layout(fig):
    layout = go.Layout(
        title='Wind Speed',
        xaxis=dict(
            title='Time',
            titlefont_size=16,
            tickfont_size=14,
        ),
        yaxis=dict(
            title='km/h',
            titlefont_size=16,
            tickfont_size=14,
            range=[0, 80],
        ),
        legend=dict(
            x=0,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)'
        ),
    )
    fig.update_layout(layout)



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
