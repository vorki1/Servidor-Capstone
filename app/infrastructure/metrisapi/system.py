from metrisapi.base import json_response, MetrisClient


class SystemClient(MetrisClient):
    # @json_response
    def get_environment_variable(self, name):
        uri = f'{self.base_uri}/api/system/specificenvironmentvariables'
        return self.session.post(uri, data=f'"{name}"', headers=self._get_headers())
        