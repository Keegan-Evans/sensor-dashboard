from sensor_dashboard.connection import get_queried_df
import pytest
import os

from datetime import date, datetime

test_filepath =os.path.join("test_sensor_data.db")


def test_basic_connection_no_limit():
    qdf = get_queried_df(db_fp=test_filepath, number_of_observations=None, drop_zeros=False)
    assert qdf['time'].count() == 76026

def test_basic_connection_default_cnt():
    qdf = get_queried_df(db_fp=test_filepath, number_of_observations=1000)
    assert qdf['time'].count() == 1000

def test_eliminate_zero_obs():
    queried_df = get_queried_df(db_fp=test_filepath, number_of_observations=None, drop_zeros=True)
    assert queried_df['time'].count() == 44754

def test_raises_error_wrong_start_date_type():
    with pytest.raises(ValueError):
        get_queried_df(db_fp=test_filepath, start_date="not a start date")

def test_subsets_by_start_date():
    start_date = date(2023, 10, 31)
    queried_df = get_queried_df(db_fp=test_filepath, start_date=start_date)
    assert queried_df['time'].min() >= date(2023, 10, 31)

def test_subsets_by_end_date():
    end_date = date(2023, 11, 8)
    queried_df = get_queried_df(db_fp=test_filepath, end_date=end_date)

    assert queried_df['time'].max() == end_date

def test_subsets_by_start_and_end_date():
    start_date = date(2023, 10, 31)
    end_date = date(2023, 11, 8)
    queried_df = get_queried_df(db_fp=test_filepath, start_date=start_date, end_date=end_date)

    assert queried_df['time'].min() == start_date
    assert queried_df['time'].max() == end_date

def test_subset_by_single_day():
    test_day = date(2023, 10, 31)
    queried_df = get_queried_df(db_fp=test_filepath, start_date=test_day, end_date=test_day)
    
    for thing in queried_df['time']:
        print(thing.date())

    assert queried_df['time'].map( lambda day : day == test_day).all()
