import os
from sqlalchemy import create_engine, select
from sqlalchemy.orm import joinedload
from mqtt_data_logger.sensor_data_models import SensorMeasurement
import pandas as pd

default_fp = os.path.join("/", "home", "beta", "sensor_data.db")

# Session = sessionmaker(bind=sqlite_engine)


def get_queried_df(db_fp=default_fp):

    sqlite_engine = create_engine(f"sqlite:///{db_fp}")

    with sqlite_engine.connect() as connection:
        query = select(SensorMeasurement).options(
                                        joinedload(SensorMeasurement.topic),
                                        joinedload(SensorMeasurement.sensor),
                                        joinedload(SensorMeasurement.
                                                   measurement)).limit(1000)
        queried_df = pd.read_sql_query(query, connection)

        return queried_df


if __name__ == '__main__':
    results = get_queried_df()
    print(results.head())
