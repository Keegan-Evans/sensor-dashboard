import os
from sqlalchemy import create_engine, select, or_
from sqlalchemy.orm import joinedload
from mqtt_data_logger.sensor_data_models import SensorMeasurement, Measurement
import pandas as pd
import datetime as dt
from icecream import ic
from sensor_dashboard.util import limit_observations
# import numpy as np

default_fp = os.path.join("/", "home", "beta", "sensor_data.db")
testing_fp = os.path.join("sensor_dashboard", "tests", "data", "test_data.db")


# def get_queried_df(db_fp=default_fp, number_of_observations=1000, drop_zeros=True, start_date=None, end_date=None, target_measurement=None):
    # """
    # db_fp: path to the database file. By default, this is the path to `sensor_dashboard/home/beta/sensor_data.db` by `connection.py`.
# 
    # In charge of querying the database and returning a pandas dataframe of the most recent 1000 records.
    # """
    # ic()
# 
    # dt_start_date = dt.datetime.fromtimestamp(start_date)
    # dt_end_date = dt.datetime.fromtimestamp(end_date)
# 
    # sqlite_engine = create_engine(f"sqlite:///{db_fp}")
# 
    # TODO: setup interface for selecting different data ranges
    # instead of just the most recent 1000 records.
    # with sqlite_engine.connect() as connection:
        # query = select(SensorMeasurement)\
            # .join(Measurement, onclause=SensorMeasurement.measurement)\
            # .options(joinedload(SensorMeasurement.topic),
                    #  joinedload(SensorMeasurement.sensor),
                    #  joinedload(SensorMeasurement.
                                # measurement))\
            # .order_by(SensorMeasurement.time.asc())
        # 
# 
        # if drop_zeros:
            # query = query.where(SensorMeasurement.value > 0)
# 
        # if dt_start_date:
            # if not isinstance(dt_start_date, dt.date):
                # raise ValueError(
                    # "Provided value({}) for `start_date` is type "
                    # "{}, not datetime.date.".format(
                        # start_date, type(start_date)))
            # query = query.where(SensorMeasurement.time >= dt_start_date)
# 
        # if dt_end_date:
            # if not isinstance(dt_end_date, dt.date):
                # raise ValueError(
                    # "Provided value({}) for `end_date` is type "
                    # "{}, not datetime.date.".format(
                        # end_date, type(end_date)))
            # query = query.where(SensorMeasurement.time <= dt_end_date)
        # 
        # if target_measurement:
#             # query = query.where(Measurement.measurement == target_measurement)
#         # 
#         TODO: this is crappy and fragile
#         subset for less data passing
#         info_results = connection.execute(query)
#         total_entries_so_far = info_results.rowcount
#         ic(total_entries_so_far)
#         total_entries_so_far = connection.execute(query).scalar()
#         ic(total_entries_so_far)
#         ic(dir(connection.execute(query)))
#         first_entry = connection.execute(query).first()[0]
#         last_entry= connection.execute(query).lastrowid
#         last_entry = connection.execute(
#             query.order_by(SensorMeasurement.time.desc())).first()[0]
#         ic(first_entry, last_entry)
#         # 
# # 

#             TODO: better way to calculate selected ids
#             query = query.where(
#                 SensorMeasurement.sensor_measurement_num_id.in_(selection_ids))

#             ic(str(query))
# # 
#             query = query.limit(number_of_observations)
#         # 
        # queried_df = pd.read_sql_query(query, connection)
# 
        # queried_df = limit_observations(queried_df, number_of_observations)   
# 
        # if queried_df.empty:
            # raise ValueError("No data found for the provided date range.")
        # return queried_df
# 
# 

def get_queried_df(db_fp=default_fp, number_of_observations=1000, drop_zeros=True, start_date=None, end_date=None, target_measurement=None):
    """
    db_fp: path to the database file. By default, this is the path to `sensor_dashboard/home/beta/sensor_data.db` by `connection.py`.

    In charge of querying the database and returning a pandas dataframe of the most recent 1000 records.
    """
    ic()
    # right_now()

    dt_start_date = dt.datetime.fromtimestamp(start_date)
    dt_end_date = dt.datetime.fromtimestamp(end_date)
    eod = dt.datetime(year=dt_end_date.year,
                      month=dt_end_date.month,
                      day=dt_end_date.day,
                      hour=23,
                      minute=59,
                      second=59
                      )
    start_day = eod - dt.timedelta(weeks=2, days=1, seconds=-1)

    sqlite_engine = create_engine(f"sqlite:///{db_fp}")

    query = select(SensorMeasurement)\
        .join(Measurement, onclause=SensorMeasurement.measurement)\
        .options(joinedload(SensorMeasurement.topic),
                 joinedload(SensorMeasurement.sensor),
                 joinedload(SensorMeasurement.
                            measurement))\
        .order_by(SensorMeasurement.time.asc()).where(SensorMeasurement.time.between(start_day, eod)).where(SensorMeasurement.value > 0)
    with sqlite_engine.connect() as connection:
        queried_df = pd.read_sql_query(query, connection)    
        return queried_df
                         
                         