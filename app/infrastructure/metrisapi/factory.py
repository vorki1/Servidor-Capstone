from metrisapi.account import AccountClient
from metrisapi.configuration import ConfigurationClient
from metrisapi.dataanalysis import DataAnalysisClient
from metrisapi.historian import HistorianClient

from typing import Callable, Optional

class ClientFactory:
    def __init__(self, base_uri: str, token: Callable[[], Optional[str]]=lambda: None, verify: bool=False):
        self.account = AccountClient(base_uri, token, verify)
        self.configuration = ConfigurationClient(base_uri, token, verify)
        self.dataanalysis = DataAnalysisClient(base_uri, token, verify)
        self.historian = HistorianClient(base_uri, token, verify)