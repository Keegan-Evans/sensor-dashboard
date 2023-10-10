import unittest
from ..munge_and_plot.munge_and_plot import (
    create_wind_polar_plot, create_wind_speed_plot,
    lookup_binned_dir_midpoints, add_cardinal_midpoints_column,
    generate_frequency_by_cardinal, bin_speed_by_beaufort,
    generate_frequency_by_cardinal_and_strength, bin_direction_to_cardinal,
    munge_wind_data, create_rainfall_plot, just_wind_data
)
import plotly.graph_objects as go
import pandas as pd

from ..connection.connection import get_queried_df

test_degree_directions = []

test_wind_directions = ['N', 'N', 'NNE', 'NE', 'NE', 'ENE', 'ENE', 'E', 'E',
                        'ESE', 'SE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'SW',
                        'WSW', 'W', 'W', 'WNW', 'NW', 'NW', 'NW', 'NNW',
                        'NNW']

expected_cardinal_frequency = {'N': 2, 'NNE': 1, 'NE': 2, 'ENE': 2, 'E': 2,
                               'ESE': 1, 'SE': 2, 'SSE': 1, 'S': 1, 'SSW': 1,
                               'SW': 2, 'WSW': 1, 'W': 2, 'WNW': 1, 'NW': 3,
                               'NNW': 2}

wind_speeds = [0, 1, 2, 5, 6, 11, 12, 19, 20, 28, 29, 38, 39, 49, 50, 61, 62,
               74, 75, 88, 89, 102, 103, 117, 118, 195]

expected_beaufort = ['Calm', 'Calm',
                     'Light Air', 'Light Air',
                     'Light Breeze', 'Light Breeze',
                     'Gentle Breeze', 'Gentle Breeze',
                     'Moderate Breeze', 'Moderate Breeze',
                     'Fresh Breeze', 'Fresh Breeze',
                     'Strong Breeze', 'Strong Breeze',
                     'Near Gale', 'Near Gale',
                     'Gale', 'Gale',
                     'Strong Gale', 'Strong Gale',
                     'Storm', 'Storm',
                     'Violent Storm', 'Violent Storm',
                     'Hurricane Force', 'Hurricane Force'
                     ]

expected_midpoints = [0.0, 0.0, 22.5, 45.0, 45.0, 67.5, 67.5, 90.0, 90.0,
                      112.5, 135.0, 135.0, 157.5, 180.0, 202.5, 225.0, 225.0,
                      247.5, 270.0, 270.0, 292.5, 315.0, 315.0, 315.0, 337.5,
                      337.5]


class test_polar(unittest.TestCase):
    def setUp(self) -> None:

        self.wind_test_df = pd.DataFrame({
            'wind_direction': test_wind_directions,
            'wind_speed': wind_speeds,
        })

        self.wind_test_beaufort_midpoints_df = self.wind_test_df.copy()
        bin_speed_by_beaufort(self.wind_test_beaufort_midpoints_df,
                              'wind_speed')
        add_cardinal_midpoints_column(self.wind_test_beaufort_midpoints_df,
                                      'wind_direction')

        self.wind_test_full = generate_frequency_by_cardinal_and_strength(
            self.wind_test_beaufort_midpoints_df.copy(),
            'wind_direction',
            'beaufort')
        return super().setUp()

    def test_df(self):
        self.assertIsInstance(self.wind_test_df, pd.DataFrame)

    def test_lookup_midpoints(self):
        mapped_midpoints = map(lookup_binned_dir_midpoints,
                               self.wind_test_df['wind_direction']
                               )
        self.assertEqual(list(mapped_midpoints), expected_midpoints)

    def test_map_cardinal_midpoints(self):
        add_cardinal_midpoints_column(self.wind_test_df, 'wind_direction')
        self.assertIsNotNone(self.wind_test_df['cardinal_midpoints_column'])
        self.assertEqual(
            list(self.wind_test_df['cardinal_midpoints_column'],),
            expected_midpoints

        )

    def test_bin_speed_by_beaufort(self):
        bin_speed_by_beaufort(self.wind_test_df, 'wind_speed')
        self.assertIsNotNone(self.wind_test_df['beaufort'])
        self.assertEqual(
            list(self.wind_test_df['beaufort']),
            expected_beaufort
        )

    def test_generate_frequency_by_cardinal(self):
        generate_frequency_by_cardinal(self.wind_test_df, 'wind_direction')
        self.assertIsNotNone(self.wind_test_df['frequency_by_cardinal'])

        def check_freq(x: pd.Series) -> bool:
            obs_freq = x.loc['frequency_by_cardinal']
            exp_freq = expected_cardinal_frequency[x.loc['wind_direction']]
            return obs_freq == exp_freq

        self.assertTrue(self.wind_test_df.apply(check_freq, axis=1).all())

    def test_generate_frequency_by_cardinal_and_strength(self):
        self.wind_test_beaufort_midpoints_df = \
            generate_frequency_by_cardinal_and_strength(
                self.wind_test_beaufort_midpoints_df,
                'wind_direction',
                'beaufort')

        self.assertIsNotNone(
            self.wind_test_beaufort_midpoints_df[
                'frequency_by_cardinal_and_strength']
            )

        self.assertEqual(self.wind_test_beaufort_midpoints_df.columns.tolist(),
                         ['wind_direction', 'wind_speed', 'beaufort',
                          'cardinal_midpoints_column',
                          'frequency_by_cardinal_and_strength']
                         )

    def test_create_wind_polar_plot(self):
        fig = create_wind_polar_plot(self.wind_test_full)
        self.assertIsInstance(fig, go.Figure)


class TestArrangeWindData(unittest.TestCase):
    def setUp(self):
        self.raw_df = get_queried_df()
        self.wind_df = just_wind_data(self.raw_df)

    def test_setup(self):
        self.assertIsInstance(self.raw_df, pd.DataFrame)

    def test_add_cardinal_midpoints_column(self):
        add_cardinal_midpoints_column(self.wind_df, 'cardinal_direction')
        self.assertIsInstance(self.wind_df, pd.DataFrame)
        for column_label in self.wind_df.columns.to_list():
            self.assertIn(column_label,
                          ['time', 'measurement', 'value', 'beaufort',
                           'cardinal_direction', 'wind_direction',
                           'cardinal_midpoints_column'])
        self.assertEqual(self.wind_df.shape, (50, 4))

    def test_direction_to_cardinal(self):
        wind_dir_df = self.raw_df.where(
            self.raw_df['measurement'] == 'wind_direction').dropna()
        print(wind_dir_df)
        wind_dir_df = wind_dir_df.rename(columns={'value': 'wind_direction'})
        print(wind_dir_df)
        bin_direction_to_cardinal(wind_dir_df, 'wind_direction')
        self.assertIsInstance(wind_dir_df, pd.DataFrame)
        self.assertIn('cardinal_direction', wind_dir_df.columns.to_list())

    def test_munge_to_wind_df(self):
        wind_df = munge_wind_data(self.raw_df)
        self.assertIsInstance(wind_df, pd.DataFrame)
        self.assertEqual(wind_df.columns.tolist(),
                         ['time', 'beaufort', 'cardinal_direction',
                          'frequency_by_cardinal_and_strength',
                          'cardinal_midpoints_column'])
        self.assertEqual(wind_df.shape, (50, 5))

    def test_create_wind_speed_plot(self):
        wind_spd_plot = create_wind_speed_plot(self.raw_df)
        self.assertIsInstance(wind_spd_plot, go.Figure)

    def test_create_rainfall_plot(self):
        rainfall_plot = create_rainfall_plot(self.raw_df)
        self.assertIsInstance(rainfall_plot, go.Figure)
