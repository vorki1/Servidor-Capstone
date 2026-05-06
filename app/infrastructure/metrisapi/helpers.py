from datetime import datetime
from dateutil.parser import parse
from dateutil.tz import tz
from dateutil.tz.win import tzwin

def process_trend_values(trend_values, timezone:str = None):
    xs = [convert_datetime_to_given_timezone(parse(xy['x']), timezone) if 'x' in xy else f'{datetime.min}' for xy in trend_values]
    ys = [xy['y'] if 'y' in xy else 0.0 for xy in trend_values]

    return xs, ys


def process_raw_trend_values(trend_values):
    """
    Hotfix when pulling raw data via Metris API: the final value is provided a random number of times
    if resolution == 0 and interpolation_resolution_type == InterpolationResolutionType.ticks
    """
    trend_value_last = trend_values[-1]
    while True:
        if len(trend_values) < 2:
            return trend_values
        if not trend_value_last['x'] == trend_values[-1]['x'] == trend_values[-2]['x']:
            return trend_values
        trend_values.pop(-1)


def map_id_to_tag(tag_list, tags):
    tag_id_tuples = [(t['name'], t['id']) for t in tags if tag_name_wanted(tag_name=t['name'], tag_list=tag_list)]
    return dict(tag_id_tuples)


def tag_name_wanted(tag_name, tag_list):
    if tag_name in tag_list:
        return True
    else:
        return False


def tags_by_name(desired_tags:list, tags:list):
    return [t for t in tags if t['name'] in desired_tags]

    
def convert_datetime_to_given_timezone(time: datetime, timezone:str = None):
    if timezone:
        return time.astimezone(tzwin(timezone))
    return time.astimezone(tz.tzlocal())