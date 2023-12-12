# from sensor_dashboard.connection import get_queried_df
# import pytest
# import os

# from datetime import date, datetime

# test_filepath =os.path.join("test_sensor_data.db")


# def test_basic_connection_no_limit():
#     qdf = get_queried_df(db_fp=test_filepath, number_of_observations=None, drop_zeros=False)
#     assert qdf['time'].count() == 76026

# def test_basic_connection_default_cnt():
#     qdf = get_queried_df(db_fp=test_filepath, number_of_observations=1000)
#     assert qdf['time'].count() == 1000

# def test_eliminate_zero_obs():
#     queried_df = get_queried_df(db_fp=test_filepath, number_of_observations=None, drop_zeros=True)
#     assert queried_df['time'].count() == 44754

# def test_raises_error_wrong_start_date_type():
#     with pytest.raises(ValueError):
#         get_queried_df(db_fp=test_filepath, start_date="not a start date")

# def test_subsets_by_start_date():
#     start_date = date(2023, 10, 31)
#     queried_df = get_queried_df(db_fp=test_filepath, start_date=start_date)
#     assert queried_df['time'].min() >= date(2023, 10, 31)

# def test_subsets_by_end_date():
#     end_date = date(2023, 11, 8)
#     queried_df = get_queried_df(db_fp=test_filepath, end_date=end_date)

#     assert queried_df['time'].max() == end_date

# def test_subsets_by_start_and_end_date():
#     start_date = date(2023, 10, 31)
#     end_date = date(2023, 11, 8)
#     queried_df = get_queried_df(db_fp=test_filepath, start_date=start_date, end_date=end_date)

#     assert queried_df['time'].min() == start_date
#     assert queried_df['time'].max() == end_date

# def test_subset_by_single_day():
#     test_day = date(2023, 10, 31)
#     queried_df = get_queried_df(db_fp=test_filepath, start_date=test_day, end_date=test_day)
    
#     for thing in queried_df['time']:
#         print(thing.date())

#     assert queried_df['time'].map( lambda day : day == test_day).all()


import datetime as dt
import select
from icecream import ic
import pandas as pd
import unittest
import pytest
import sqlalchemy
from sqlalchemy import create_engine, select
import sensor_dashboard
from sensor_dashboard.connection import get_queried_df
import sensor_dashboard.tests.data as data_dir
from mqtt_data_logger.sensor_data_models import SensorMeasurement
from importlib_resources import files, as_file


class TestConnection(unittest.TestCase):
    package = 'sensor_dashboard.tests'

    def setUp(self):
        self.source = files(sensor_dashboard.tests.data).joinpath("sensor_data.db")
        ic(self.source)
        self.db_fp = as_file(self.source)
        ic(self.db_fp)
        # with as_file(self.source) as db_fp:
        self.engine = create_engine("sqlite:///{}".format(self.db_fp))
        ic(self.engine)

            # importlib_resources.files(data_dir).joinpath("sensor_data.db"))
        # ic(dir(self.db_fp))
        # self.engine = create_engine(f"sqlite:///{self.db_fp}")

    def test_connect(self):
        # with as_file(self.source) as db_fp:
            # engine = create_engine("sqlite:///{}".format(db_fp))
        ic(sqlalchemy.inspect(self.engine).get_table_names())
        try:
            self.engine.connect()
        except Exception as e:
            raise e

    def test_retrieve_data_keep_zeros(self):
        with self.engine.connect() as connection:
            start_date = dt.datetime(2023, 10, 1).timestamp()
            end_date = dt.datetime(2023, 12, 11).timestamp()
            ic(start_date)
            ic(end_date)

            df = get_queried_df(db_fp=self.source,
                                number_of_observations=1000,
                                drop_zeros=False,
                                start_date=start_date,
                                end_date=end_date)

            ic(df)
            assert len(df) == 1000

    def test_retrieve_data_drop_zeros(self):
        with self.engine.connect() as connection:
            start_date = dt.datetime(2023, 10, 1).timestamp()
            end_date = dt.datetime(2023, 12, 11).timestamp()
            ic(start_date)
            ic(end_date)

            df = get_queried_df(db_fp=self.source,
                                number_of_observations=1000,
                                drop_zeros=True,
                                start_date=start_date,
                                end_date=end_date)

            ic(df)
            assert len(df) == 813

    def test_retrieve_data_subset_to_one_day(self):
        with self.engine.connect() as connection:
            start_date = dt.datetime(2023, 12, 1).timestamp()
            end_date = dt.datetime(2023, 12, 2).timestamp()
            ic(start_date)
            ic(end_date)

            df = get_queried_df(db_fp=self.source,
                                number_of_observations=1000,
                                drop_zeros=True,
                                start_date=start_date,
                                end_date=end_date)

            assert len(df) == 72