import os
from colorama import colorama_text
from sqlalchemy import create_engine, select
from sqlalchemy.orm import joinedload
from mqtt_data_logger.sensor_data_models import SensorMeasurement
import pandas as pd
import datetime as dt
from icecream import ic

default_fp = os.path.join("/", "home", "beta", "sensor_data.db")
testing_fp = os.path.join("sensor_dashboard", "tests", "data", "sensor_data.db")




def get_queried_df(db_fp=default_fp, number_of_observations=1000, drop_zeros=True, start_date=None, end_date=None):
    """
    db_fp: path to the database file. By default, this is the path to `sensor_dashboard/home/beta/sensor_data.db` by `connection.py`.

    In charge of querying the database and returning a pandas dataframe of the most recent 1000 records.
    """

    dt_start_date = dt.datetime.fromtimestamp(start_date)
    dt_end_date = dt.datetime.fromtimestamp(end_date)


    sqlite_engine = create_engine(f"sqlite:///{db_fp}")

    # TODO: setup interface for selecting different data ranges, instead of just the most recent 1000 records.
    with sqlite_engine.connect() as connection:
        query = select(SensorMeasurement).options(
                                        joinedload(SensorMeasurement.topic),
                                        joinedload(SensorMeasurement.sensor),
                                        joinedload(SensorMeasurement.
                                                   measurement)) \
                                         .order_by(
                                             SensorMeasurement.time.desc()
                                             )

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
        

        # TODO: this is crappy and fragile
        # subset for less data passing
        total_entries_so_far = connection.execute(query).scalar()
        last_entry = connection.execute(query).first()[0]


        # ic(total_entries_so_far)
        if total_entries_so_far > number_of_observations:
            entry_spacing = ic(max(1,
                               total_entries_so_far // number_of_observations))
            # ic(entry_spacing)
            # TODO: better way to calculate selected ids
            selection_ids = list(range(
                last_entry - total_entries_so_far,
                last_entry,
                entry_spacing
                ))
            query = query.where(
                SensorMeasurement.sensor_measurement_num_id.in_(selection_ids))

        # if number_of_observations is not None:
            # print("VAlUE OTHER THAN NONE OBSERVED")
            # query = query.limit(number_of_observations)

        # limit number only after all other selection takes place
        # match number_of_observations:
            # case None:
                # pass
            # case int():
                # query = query.limit(number_of_observations)

        queried_df = pd.read_sql_query(query, connection)
        if queried_df.empty:
            raise ValueError("No data found for the provided date range.")
        return queried_df


if __name__ == '__main__':
    results = get_queried_df()
    print(results.head())
