from requests import Session
from app.core.config import settings
from urllib3.exceptions import InsecureRequestWarning
import warnings


def supress_insecure_request_warning(fn):
    def wrapper(*args, **kwargs):
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=InsecureRequestWarning)
            return fn(*args, **kwargs)
    return wrapper


def json_response(fn):
    @supress_insecure_request_warning
    def wrapper(*args, **kwargs):
        response = fn(*args, **kwargs)
        if response.status_code == 200:
            return response.json()
        else:
            return response.raise_for_status()

    return wrapper


def callback_apply(callback):
    def decorator(fn):
        def wrapper(*args, **kwargs):
            result = fn(*args, **kwargs)
            return callback(result)
        return wrapper
    return decorator
    

def callback_map(callback):
    def decorator(fn):
        def wrapper(*args, **kwargs):
            result = fn(*args, **kwargs)
            return [callback(item) for item in result]
        return wrapper
    return decorator

class MetrisClient:
    def __init__(self, base_uri, token=lambda: None, verify=False):
        self.base_uri = base_uri
        self.token = token
        self.session = Session()
        self.session.verify = verify

    def _get_headers(self):
        bearer_token = self.token()
        if bearer_token is not None:
            return {'Authorization': f'Bearer {bearer_token}'}
        else:
            return bearer_token
