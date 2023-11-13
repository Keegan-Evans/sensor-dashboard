from sensor_dashboard.connection import get_queried_df
import pytest
import os

test_filepath =os.path.join(# "sensor-dashboard", # "tests", "data",
                            "sensor_data.db")
print(test_filepath)
print("/workspaces/sensor-dashboard/sensor_data.db")


def test_basic_connection_no_limit():
    qdf = get_queried_df(db_fp=test_filepath, number_of_observations=None, drop_zeros=False)
    print(qdf['time'])
    assert qdf['time'].count() == 76026

def test_basic_connection_default_cnt():
    qdf = get_queried_df(db_fp=test_filepath, number_of_observations=1000)
    assert qdf['time'].count() == 1000

def test_eliminate_zero_obs():
    queried_df = get_queried_df(db_fp=test_filepath, number_of_observations=None, drop_zeros=True)
    assert queried_df['time'].count() == 44754
