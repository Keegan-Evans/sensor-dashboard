
import os
from sqlite3 import DataError
from debugpy import connect
from sqlalchemy import func
from icecream import ic
from sqlalchemy import create_engine, select, Table, MetaData
from sqlalchemy.orm import joinedload, Session
from mqtt_data_logger.sensor_data_models import SensorMeasurement
import pandas as pd
import datetime as dt

# default_fp = os.path.join("/", "home", "beta", "sensor_data.db")
testing_fp = os.path.join(".", "test_db_00.db")




def get_queried_df(db_fp=testing_fp,
                   number_of_observations=2500,
                   drop_zeros=True,
                   start_date_timestamp: int | None = None,
                   end_date_timestamp: int | None = None):


    engine = create_engine(f"sqlite:///{db_fp}", echo=True)

    with engine.connect() as connection:

        date_range_query = select(SensorMeasurement.time)
        # all_dates = connection.execute(date_range_query).unique().all()
    

        if start_date_timestamp is not None:
            dt_start_date = dt.datetime.fromtimestamp(start_date_timestamp)
        else:
            dt_start_date = min([x[0] for x in connection.execute(date_range_query).all()])

        if end_date_timestamp is not None:
            dt_end_date = dt.datetime.fromtimestamp(end_date_timestamp)
        else:
            dt_end_date = max([x[0] for x in connection.execute(date_range_query).all()])

        data_query = select(SensorMeasurement).options(
                                        joinedload(
                                            SensorMeasurement.topic),
                                        joinedload(
                                            SensorMeasurement.sensor),
                                        joinedload(
                                            SensorMeasurement.measurement)
                                        ).order_by(
                                             SensorMeasurement.time.desc()
                                             ).filter(SensorMeasurement.time.between(
                                                 dt_start_date, dt_end_date
                                             ))
    

    # with Session(engine) as session:
        num_rows = connection.execute(data_query).scalar()
        ic(num_rows)
        try:
            entry_spacing = max(1, num_rows // number_of_observations)
        except Exception as e:
            ic("Trouble calculating spacing interval, this is likely because there was no data found in the database within the specified range.")
            raise e
        selection_ids = list(range(0, num_rows, entry_spacing))
        # get only records for use with selected ids
        subset_query = data_query.where(SensorMeasurement.sensor_measurement_num_id.in_(selection_ids))
# 
        subset_df = pd.read_sql(subset_query, connection)
        # subsetted = session.scalars(only_ided_rows)
        ic(subset_df)
        return subset_df





        # subset_rows = session.query(SensorMeasurement).where(SensorMeasurement.sensor_measurement_num_id.in_(selection_ids))

        
        # ic(str(subset_rows))

        # demo_query = session.scalars(query)


        # raw_data = cnx.execute(query).fetchall().count(

        # df = pd.read_sql_query(sql=query, con=cnx)
    
    # spacing = (len(df) // number_of_observations)

    


    # with create_engine(f"sqlite:///{db_fp}") as engine:
    # with engine.connect() as connection:
        # query = select(SensorMeasurement).options(
                                        # joinedload(
                                            # SensorMeasurement.topic),
                                        # joinedload(
                                            # SensorMeasurement.sensor),
                                        # joinedload(
                                            # SensorMeasurement.measurement)
                                        # ).order_by(
                                            #  SensorMeasurement.time.desc()
                                            #  ) 
                                        # .fetch(number_of_observations)
# 
        # df = pd.read_sql_query(query, connection)

    # ic(len(df))
        


    # TODO: setup interface for selecting different data ranges, instead of just the most recent 1000 records.
    # query = select(SensorMeasurement).options(
                                    # joinedload(
                                        # SensorMeasurement.topic),
                                    # joinedload(
                                        # SensorMeasurement.sensor),
                                    # joinedload(
                                        # SensorMeasurement.measurement)
                                    # ).order_by(
                                        #  SensorMeasurement.time.desc()
                                        #  )

    # if drop_zeros:
        # query = query.where(SensorMeasurement.value > 0)
# 
    # if dt_start_date:
        # if not isinstance(dt_start_date, dt.date):
            # raise ValueError("Provided value({}) for `start_date` is type {}, not datetime.date.".format(start_date_timestamp, type(start_date_timestamp)))
        # query = query.where(SensorMeasurement.time >= dt_start_date)
# 
    # if dt_end_date:
        # if not isinstance(dt_end_date, dt.date):
            # raise ValueError("Provided value({}) for `end_date` is type {}, not datetime.date.".format(end_date_timestamp, type(end_date_timestamp)))
        # query = query.where(SensorMeasurement.time <= dt_end_date)
# 
    # query = query.limit(number_of_observations)
# 
    # if number_of_observations is not None:
        # print("VAlUE OTHER THAN NONE OBSERVED")
        # query = query.limit(number_of_observations)

    # limit number only after all other selection takes place
    # match number_of_observations:
        # case None:
            # pass
        # case int():
            # query = query.limit(number_of_observations)

    # with sqlite_engine.connect() as connection:
            # queried_df = pd.read_sql_query(query, connection)

    # if queried_df.empty:
        # raise ValueError("No data found for the provided date range.")
    
    # return queried_df


def test_subsets_on_start_date():
    test_df = get_queried_df(start_date_timestamp=1699426800)
    source_dt = dt.datetime.fromtimestamp(1699426800)
    assert source_dt not in test_df.loc['time']

    ic(test_df['time'])
    assert False
    
if __name__ == '__main__':
    get_queried_df()
    # test start_date
    get_queried_df(start_date_timestamp=1699426800)
    # results = get_queried_df()
