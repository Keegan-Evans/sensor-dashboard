from sensor_dashboard.connection.connection import get_queried_df

from sensor_dashboard.munge_and_plot.munge_and_plot import (
    just_wind_data, generate_frequency_by_cardinal_and_strength,
    create_wind_polar_plot, create_wind_speed_plot, create_rainfall_plot,
    munge_wind_data
)

from plotly import graph_objects as go

import unittest
import os


class TestWindMunging(unittest.TestCase):
    def setUp(self):
        test_db_fp = os.path.join(".", "sensor_data.db")
        raw_df = get_queried_df(db_fp=test_db_fp)
        self.wind_df = munge_wind_data(raw_df)
        self.raw_df = raw_df

    def test_create_wind_df(self):
        expected_columns = ['time', 'value_speed', 'value_dir',
                            'str_value_speed', 'str_value_dir']
        wind_df = just_wind_data(self.raw_df)

        for col in expected_columns:
            assert col in wind_df.columns

    def test_generate_freq(self):
        
        freq_df = generate_frequency_by_cardinal_and_strength(
            just_wind_data(self.raw_df),
            cardinal_dir_col='str_value_dir',
            beaufort_col='str_value_speed'
        )

        expected_columns = ['time', 'beaufort', 'cardinal_direction',
                            'cardinal_midpoints',
                            'proportion_frequency_by_cardinal_and_strength']

        for column in expected_columns:
            assert column in freq_df.columns
    
    def test_munge_wind_data(self):
        wind_df = munge_wind_data(self.raw_df)
        expected_columns = ['time', 'beaufort', 'cardinal_direction',
                            'cardinal_midpoints',
                            'proportion_frequency_by_cardinal_and_strength']

        for column in expected_columns:
            assert column in wind_df.columns

    def test_create_wind_polar_plot(self):
        fig = create_wind_polar_plot(self.wind_df)
        assert isinstance(fig, go.Figure)

    def test_wind_speed_plot(self):
        fig = create_wind_speed_plot(self.raw_df)
        assert isinstance(fig, go.Figure)
    
    def test_rainfall_plot(self):
        fig = create_rainfall_plot(self.raw_df)

        fig.show()
