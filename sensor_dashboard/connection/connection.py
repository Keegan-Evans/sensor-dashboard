import os
from sqlalchemy import create_engine, select, desc
from sqlalchemy.orm import joinedload
from mqtt_data_logger.sensor_data_models import SensorMeasurement
import pandas as pd

default_fp = os.path.join("/", "home", "beta", "sensor_data.db")

# Session = sessionmaker(bind=sqlite_engine)


def get_queried_df(db_fp=default_fp):

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
                                                   measurement)).order_by(SensorMeasurement.time.desc()).limit(1000)
        queried_df = pd.read_sql_query(query, connection)

        return queried_df


if __name__ == '__main__':
    results = get_queried_df()
    print(results.head())
