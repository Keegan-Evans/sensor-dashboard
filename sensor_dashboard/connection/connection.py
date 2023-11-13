import os
from sqlalchemy import create_engine, select, desc
from sqlalchemy.orm import joinedload
from mqtt_data_logger.sensor_data_models import SensorMeasurement
import pandas as pd
import pytest

default_fp = os.path.join("/", "home", "beta", "sensor_data.db")
testing_fp = os.path.join(".", "sensor_data.db")

# Session = sessionmaker(bind=sqlite_engine)

def get_queried_df(db_fp=testing_fp, number_of_observations=None, drop_zeros=True):

    """
    db_fp: path to the database file. By default, this is the path to `sensor_dashboard/home/beta/sensor_data.db` by `connection.py`.

    In charge of querying the database and returning a pandas dataframe of the most recent 1000 records.
    """

    sqlite_engine = create_engine(f"sqlite:///{db_fp}")

    # TODO: setup interface for selecting different data ranges, instead of just the most recent 1000 records.
    with sqlite_engine.connect() as connection:
        query = select(SensorMeasurement).options(
                                        joinedload(SensorMeasurement.topic),
                                        joinedload(SensorMeasurement.sensor),
                                        joinedload(SensorMeasurement.
                                                   measurement)).order_by(SensorMeasurement.time.desc())

        match number_of_observations:
            case None:
                pass
            case int():
                query = query.limit(number_of_observations)

        if drop_zeros:
            query = query.where(SensorMeasurement.value > 0)
            
                
        # if number_of_observations is not None:
            # print("VAlUE OTHER THAN NONE OBSERVED")
            # query = query.limit(number_of_observations)


        queried_df = pd.read_sql_query(query, connection)
        return queried_df


if __name__ == '__main__':
    results = get_queried_df()
    print(results.head())
