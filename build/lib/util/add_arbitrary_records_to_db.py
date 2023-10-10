import time
from mqtt_data_logger import add_sensors_reading_record
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import random
import os
import sys


# setup ability to interact with db
# an Engine, which the Session will use for connection
# resources, typically in module scope
def create_session(database_fp):
    engine = create_engine("sqlite:///{}".format(database_fp))

    # a sessionmaker(), also in the same scope as the engine
    Session = sessionmaker(engine)
    Session = Session()
    return Session


# generate the records
def get_wind_speed(min=0, max=49):
    return random.randint(0, 22) + round(random.random(), 3)


def get_wind_direction(min=0, max=360):
    return random.randint(min, max)


def get_rainfall():
    return round(random.random(), 2)


def get_fake_reading():
    return {
        "wind_speed": get_wind_speed(),
        "wind_direction": get_wind_direction(),
        "rainfall": get_rainfall(),
    }


def get_fake_readings(num_readings):
    return [
        get_fake_reading() for _ in range(num_readings)
    ]


spoofed_readings = get_fake_readings(num_readings=50)


# add records to db
def add_readings_to_db(Session, readings):
    for reading in readings:
        add_sensors_reading_record(session=Session,
                                   topic='sensor_data/weather',
                                   sensor='test_data_sensor',
                                   measurements=reading)
        print("added reading: {}".format(reading))
        time.sleep(random.randint(1, 15))

# # we can now construct a Session() without needing to pass the
# # engine each time
# with Session() as session:
#     session.add(some_object)
#     session.add(some_other_object)
#     session.commit()
# # closes the session


if __name__ == "__main__":
    add_readings_to_db(create_session(os.path.join(sys.argv[1])),
                       spoofed_readings)
