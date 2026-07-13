from app.infrastructure.metrisapi.base import callback_apply, json_response, MetrisClient
from app.infrastructure.metrisapi.datetimehelpers import convert_datetime_to_isoformat
from dateutil import tz
from datetime import datetime
from dateutil import tz
from datetime import datetime
import dateutil.parser

tzwl = tz.gettz("America/Santiago")
import dateutil.parser

def ticks_from(hours=0, minutes=0, seconds=0):
    ts = 10_000_000
    return (hours * 3600 * ts) + (minutes * 60 * ts) + (seconds * ts)


class InterpolationMethod:
    step = 0
    linear = 1
    cubic_spline_robust = 7


class InterpolationResolutionType:
    points = 0
    ticks = 1


class AggregateFunction:
    average = 0
    minimum = 1
    maximum = 2
    median = 3
    variance = 4
    standard_deviation = 5
    last = 6
    sum = 7
    count = 8


class TrendValuesParameters:
    # time_shift for 2020.R3+ only accepts int and not also float like till 2020.R2.SP4
    def __init__(self, tag_id, start, end, time_shift: int = 0,
                 interpolation_method: InterpolationMethod = InterpolationMethod.linear,
                 interpolation_resolution: int = 1080,
                 interpolation_resolution_type: InterpolationResolutionType = InterpolationResolutionType.points,
                 aggregate_function: AggregateFunction = AggregateFunction.average,
                 tracking_reference_step: int = None):
        self.tag_id = tag_id
        self.start = start
        self.end = end
        self.time_shift = time_shift
        self.interpolation_method = interpolation_method
        self.interpolation_resolution = interpolation_resolution
        self.interpolation_resolution_type = interpolation_resolution_type
        self.aggregate_function = aggregate_function
        self.tracking_reference_step = tracking_reference_step

    def as_querystring_dictionary(self):
        return {
            'tagid': self.tag_id,
            'start': f'{self.start}',
            'end': f'{self.end}',
            'timeshift': self.time_shift,
            'interpolationmethod': self.interpolation_method,
            'interpolationresolution': self.interpolation_resolution,
            'interpolationresolutiontype': self.interpolation_resolution_type,
            'aggregatefunction': self.aggregate_function,
            'trackingreferencestep': self.tracking_reference_step,
        }


def fix_tag_value(value: dict) -> dict:
    return {
        'value': 0.0,
        'valueLast': 0.0,
        **value
    }


def fix_tag_values(values: list) -> list:
    values = [fix_tag_value(tv) for tv in values]
    for d in values:
        d.update((k, dateutil.parser.isoparse(v).astimezone(tzwl).isoformat()) for k, v in d.items() if ((k == "timestamp") or (k == "timestampLast")))
    return values


def fix_trend_value(value: dict) -> dict:
    if 't' in value:
        value['x'] = value['t']
        del value['t']
    
    if 'v' in value:
        value['y'] = value['v']
        del value['v']
    elif 'st' in value:
        value['y'] = value['st']
        del value['st']
        
    return {
        'y': 0.0,
        **value
    }


def fix_trend_values(values: list) -> list:
    values = [fix_trend_value(v) for v in values]
    for d in values:
        d.update((k, datetime.fromtimestamp(v/1000, tz = tz.UTC).astimezone(tzwl).isoformat()) for k, v in d.items() if k == "x")
    values = sorted(values, key=lambda v: v['x'])

    return values


class HistorianClient(MetrisClient):

    @callback_apply(fix_trend_values)
    @json_response
    def get_trend_values(self, trend_values_parameters):
        uri = f'{self.base_uri}/api/historian/v02/trendvalues'
        trend_values_parameters.start = convert_datetime_to_isoformat(trend_values_parameters.start)
        trend_values_parameters.end = convert_datetime_to_isoformat(trend_values_parameters.end)
        params = trend_values_parameters.as_querystring_dictionary()

        return self.session.get(uri, headers=self._get_headers(), params=params)


    @callback_apply(fix_tag_values)
    @json_response
    def get_tag_values(self, ids):
        uri = f'{self.base_uri}/api/historian/v02/tagvalues'
        params = {'ids': ids}
        return self.session.get(uri, headers=self._get_headers(), params=params)    
    
    @json_response
    def get_trend_average(self, id, start, end):
        uri = f'{self.base_uri}/api/historian/v02/trends/{id}/average'
        params = {'start': start, 'end': end}
        return self.session.get(uri, headers=self._get_headers(), params=params)    

    @json_response
    def post_tag_values(self, tag_values):
        uri = f'{self.base_uri}/api/historian/v02/tagvalues'
        data = tag_values
        return self.session.post(uri, headers=self._get_headers(), json=data)

    @json_response
    def get_trend_hybrid(self, id, start, end):
        start = convert_datetime_to_isoformat(start)
        end = convert_datetime_to_isoformat(end)
        uri = f'{self.base_uri}/api/historian/v02/trendhybrid/{id}?start={start}&end={end}'
        return self.session.get(uri, headers=self._get_headers())