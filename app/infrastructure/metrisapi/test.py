import pandas as pd

from metrisapi.account import AccountClient
from metrisapi.base import MetrisClient, supress_insecure_request_warning
from metrisapi.historian import TrendValuesParameters, InterpolationMethod, InterpolationResolutionType, \
    AggregateFunction, HistorianClient
from metrisapi.producttracker import ProductTrackerClient

# class TestClient(MetrisClient):
#     @supress_insecure_request_warning
#     def test(self):
#         uri = f'{self.base_uri}/api/test'
#         return self.session.get(uri)
#
# class TestHistorianClient(MetrisClient):
#     def post_tag_values(self, tag_values):
#         uri = f'{self.base_uri}/api/historian/tagvalues'
#         data = tag_values
#         print(data)
#         return data
#         # return self.session.post(uri, headers=self._get_headers(), json=data)



base_uri = 'https://172.24.252.114:9000'
ac = AccountClient(base_uri)
token = ac.authenticate(username="opp", password="*")['id']

hc = ProductTrackerClient(base_uri, lambda: token)
a = hc.get_stepid_from_tag(93,299)

tvp = TrendValuesParameters(
    tag_id=270,
    start='2021-03-17 16:00:00',
    end='2021-03-20 00:00:00',
    time_shift=0,
    interpolation_method=InterpolationMethod.linear,
    interpolation_resolution=600*10000000,
    interpolation_resolution_type=InterpolationResolutionType.ticks,
    aggregate_function=AggregateFunction.average,
    tracking_reference_step=200
)

res = hc.get_timeshifting_table(tvp, raw_data=True)

import pandas as pd
hc1 = HistorianClient(base_uri, lambda: token)
data = hc1.get_trend_values(tvp)
data = pd.DataFrame(data)
