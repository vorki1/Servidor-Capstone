from datetime import datetime
from dateutil.parser import parse
from dateutil.tz import tz, tzlocal


def convert_datetime_to_isoformat(time: datetime):
    if type(time) is str:
        time = parse(str(time))
    return time.astimezone(tz.gettz('UTC')).isoformat()


def get_current_timezone_offset_seconds():
    current_time = datetime.now(tzlocal())
    return current_time.utcoffset().total_seconds()


def get_current_utc_offset_seconds():
    timezone_offset_seconds = get_current_timezone_offset_seconds()

    current_time = datetime.now(tzlocal())
    daylight_offset_seconds = current_time.dst().total_seconds()
    
    return timezone_offset_seconds + daylight_offset_seconds