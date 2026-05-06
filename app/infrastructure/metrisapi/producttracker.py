from dateutil import tz
from datetime import datetime

from metrisapi.base import json_response, MetrisClient, callback_apply
from metrisapi.datetimehelpers import convert_datetime_to_isoformat
from metrisapi.historian import tzwl

def fix_trend_values(values: list) -> list:
    for d in values:
        d.update((k, datetime.strptime(v, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=tz.UTC).astimezone(tzwl).isoformat()) for k, v in d.items() if k == "timestamp")
        d.update((k, datetime.strptime(v, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=tz.UTC).astimezone(tzwl).isoformat()) for k, v in d.items() if k == "timestampOrigin")

    return values


class ProductTrackerClient(MetrisClient):

    @json_response
    def get_stepid_from_tag(self, step_id, tag_id):
        uri = f'{self.base_uri}/api/producttracker/process/steps/{step_id}/stepfromtag/{tag_id}'
        return self.session.get(uri, headers=self._get_headers())

    @callback_apply(fix_trend_values)
    @json_response
    def get_timeshifting_table(self, trend_values_parameters, raw_data=False):
        uri = f'{self.base_uri}/api/producttracker/process/shiftingtable/{raw_data}'
        trend_values_parameters.start = convert_datetime_to_isoformat(trend_values_parameters.start)
        trend_values_parameters.end = convert_datetime_to_isoformat(trend_values_parameters.end)
        params = trend_values_parameters.as_querystring_dictionary()
        params['trackingreferencestep'] = 0 if params['trackingreferencestep'] == None else params['trackingreferencestep']

        return self.session.post(uri, headers=self._get_headers(), json=params)



