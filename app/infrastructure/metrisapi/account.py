from metrisapi.base import json_response, MetrisClient

class AccountClient(MetrisClient):
    @json_response
    def authenticate(self, username, password):
        uri = f'{self.base_uri}/api/account/authenticate'
        data = {'username': username, 'password': password}
        return self.session.post(uri, json=data)

    @json_response
    def validate_token(self, token):
        uri = f'{self.base_uri}/api/account/validatetoken'
        return self.session.post(uri, json=token)
    
    def is_metris_open(self):
        uri = f'{self.base_uri}/api/test'
        return self.session.get(uri)