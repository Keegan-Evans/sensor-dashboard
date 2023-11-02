import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

dirs = ('N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW')

card_dirs_lookup = {
    'N': 0,
    'NNE': 22.5,
    'NE': 45,
    'ENE': 67.5,
    'E': 90,
    'ESE': 112.5,
    'SE': 135,
    'SSE': 157.5,
    'S': 180,
    'SSW': 202.5,
    'SW': 225,
    'WSW': 247.5,
    'W': 270,
    'WNW': 292.5,
    'NW': 315,
    'NNW': 337.5,
}

card_dirs = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW',
             'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']

card_dir_breaks = [0, 22.5, 45, 67.5, 90, 112.5, 135, 157.5, 180, 202.5,
                   225, 247.5, 270, 292.5, 315, 337.5, 360]

beaufort_scale = [0, 1, 5, 11, 19, 28, 38, 49, 61, 74, 88, 102, 117, 500] 

beaufort_labels = ['Calm', 'Light Air', 'Light Breeze',
                   'Gentle Breeze', 'Moderate Breeze', 'Fresh Breeze',
                   'Strong Breeze', 'Near Gale', 'Gale', 'Strong Gale',
                   'Storm', 'Violent Storm', 'Hurricane Force']


def just_wind_data(df: pd.DataFrame):
    wind_spd_df = df[df['measurement'] == 'wind_speed']
    wind_dir_df = df[df['measurement'] == 'wind_direction']
    wind_dir_df = wind_dir_df[wind_dir_df['value'] <= 360]

    binned_win = wind_spd_df.merge(wind_dir_df, on='time',
                                   suffixes=('_spd', '_dir'))

    bin_speed_by_beaufort(binned_win, 'value_spd')
    bin_direction_to_cardinal(binned_win, 'value_dir')
    return binned_win[['time', 'beaufort', 'cardinal_direction']]

    
def munge_wind_data(df: pd.DataFrame):
    # get only beaufort and cardinal direction
    binned_wind = just_wind_data(df)
    binned_w_freq = generate_frequency_by_cardinal_and_strength(
        binned_wind,
        'cardinal_direction',
        'beaufort') 

    # add midpoints for cardnial directions
    add_cardinal_midpoints_column(binned_w_freq, 'cardinal_direction')

    # add frequency by cardinal direction and beaufort
    return binned_w_freq


def generate_wind_rose_data(df):
    bin_speed_by_beaufort(df, 'wind_speed')
    bin_direction_to_cardinal(df, 'wind_direction')
    pass
    
    
def bin_direction_to_cardinal(df, dir_col):
    """Returns the cardinal direction for the provided direction."""
    df['cardinal_direction'] = pd.cut(df[dir_col],
                                      bins=card_dir_breaks,
                                      right=True,
                                      include_lowest=True,
                                      labels=card_dirs)
    return df


def lookup_binned_dir_midpoints(dir):
    """Returns the midpoint of the bin for the provided cardinal direction."""
    try:
        return card_dirs_lookup[dir]
    except KeyError:
        raise ValueError('Provided Cardinal Direction: ({}) not recognized.'
                         ' Make sure it is one of: {}'.format(
                             dir,
                             [key for key in card_dirs_lookup.keys()]
                            )
                         )


def lookup_frequency_by_direction_and_beaufort(data):
    """Returns the observed frequency of the provided data cardinal direction
    and beaufort"""
    return data


def add_cardinal_midpoints_column(df, card_dir_col):
    """Adds a column to the dataframe with the cardinal direction midpoints
    for aligning to the angular axis of a polar plot."""

    # TODO: convert from mapping on copy to mapping on original df
    df['cardinal_midpoints_column'] = df[card_dir_col].copy().map(
        lookup_binned_dir_midpoints
    )
    return df


def bin_speed_by_beaufort(df, speed_col):
    """Adds a column to a dataframe with the beaufort scale.
    df: dataframe containing wind speed data
    speed_col: name of the column containing wind speed data, in kM/h
    """
    df['beaufort'] = pd.cut(df[speed_col],
                            bins=beaufort_scale,
                            labels=beaufort_labels,
                            include_lowest=True,)


def generate_frequency_by_cardinal(df, cardinal_dir_col):
    cardinal_dirs = df[cardinal_dir_col].value_counts()
    df['frequency_by_cardinal'] = df[cardinal_dir_col].map(cardinal_dirs)
    return df


def generate_frequency_by_cardinal_and_strength(df,
                                                cardinal_dir_col,
                                                beaufort_col):
    vc = df.value_counts([cardinal_dir_col, beaufort_col], normalize=True)
    vc.name = 'frequency_by_cardinal_and_strength'
    print(vc)

    df = df.merge(vc, left_on=[cardinal_dir_col, beaufort_col],
                  right_on=[cardinal_dir_col, beaufort_col])

    df = df.rename(
        columns={'proportion': 'frequency_by_cardinal_and_strength'})

    return df


beaufort_colors = [
    "#f7f7f7", "#f0f921", "#ebd634", "#d1cf32", "#a1d059",
    "#6fc060", "#2a9d8f", "#007f5f", "#006050", "#004b7d",
    "#00326d", "#001b52", "#000028"
]


def add_trace_by_beaufort(fig, beaufort, df):
    fig.add_trace(go.Barpolar(
        r=df['frequency_by_cardinal_and_strength'].where(
            df['beaufort'] == beaufort),
        theta=df['cardinal_midpoints_column'].where(
            df['beaufort'] == beaufort),
        name=beaufort,
        width=(360/16),
        marker_color=beaufort_colors[beaufort_labels.index(beaufort)]
    ))


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


def create_wind_speed_plot(df):
    wind_spd_df = df[df.measurement == 'wind_speed']
    fig = px.scatter(wind_spd_df, x='time', y='value')
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

    