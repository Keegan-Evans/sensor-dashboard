import pytest
import datetime as dt
from icecream import ic

ic.disable()

def get_just_date_in_unix_seconds(in_dt: dt.datetime) -> int:
    time_components = [in_dt.hour * 60 ** 2, in_dt.minute * 60, in_dt.second]
    seconds_into_today = sum(time_components)
    int_dt = int(in_dt.timestamp() // 1) # floor to drop ms, then to int
# 
    ic(in_dt, time_components, seconds_into_today, int_dt)
# 
    date_in_unix_seconds = int_dt - seconds_into_today
    return date_in_unix_seconds
# 
# 
day_seconds = 60 ** 2 * 24

def get_default_dates():
    default_start = int(dt.datetime(year=2023, month=10, day=1).timestamp())
    default_end = get_just_date_in_unix_seconds(dt.datetime.now()) + day_seconds# Tests
    return default_start, default_end


def test_get_just_date_in_unix_seconds():
    todays_date_calculated = get_just_date_in_unix_seconds(dt.datetime.now())
    date_from_calculated = dt.date.fromtimestamp(todays_date_calculated)
    date_from_lib_call = dt.datetime.now().date()

    ic("Calculated: {}\nCalled: {}".format(
        date_from_calculated,
        date_from_lib_call))

    assert date_from_calculated == date_from_lib_call

def test_get_default_times():
    default_start, default_end = get_default_dates()
    ic(default_start, default_end)
    assert default_start < default_end
    assert default_end < dt.datetime.now().timestamp() + day_seconds
    assert default_end > dt.datetime.now().timestamp()

def limit_observations(df, number_of_observations):
    ic()
    num_results = len(df)
    entry_spacing = max(1,
                        num_results // number_of_observations)

        # should start at index of first entry, not zero
    selection_ids = list(range(
            0,
            num_results,
            entry_spacing
        ))
    df = ic(df.iloc[selection_ids])
    return df