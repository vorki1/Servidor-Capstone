from metrisapi.base import callback_map, json_response, MetrisClient
from metrisapi.helpers import map_id_to_tag, tags_by_name

def fix_tag_simple(tag_simple: dict) -> dict:
    return {
        'id': 0,
        'name': '',
        'description': '',
        'description2': '',
        'engUnits': '',
        'engLow': '',
        'engHigh': '',
        'enabled': True,
        'isKpiEnabled': False,
        'tagIdType': None,
        'dataType': None,
        'value': None,
        **tag_simple
    }

def fix_tag_description(tag_description: dict) -> dict:
    return {
        'id': 0,
        'name': '',
        'description': '',
        **tag_description
    }

class ConfigurationClient(MetrisClient):
    @json_response
    def get_tags(self):
        uri = f'{self.base_uri}/api/configuration/tags'
        return self.session.get(uri, headers=self._get_headers())

    @callback_map(fix_tag_description)
    @json_response
    def get_tags_description(self):
        uri = f'{self.base_uri}/api/configuration/tags/description'
        return self.session.get(uri, headers=self._get_headers())

    @callback_map(fix_tag_simple)
    @json_response
    def get_tags_simple(self):
        uri = f'{self.base_uri}/api/configuration/tags/simples'
        return self.session.get(uri, headers=self._get_headers())

    def get_tag_id_map(self, tag_names):
        tags = self.get_tags()
        return map_id_to_tag(tag_list=tag_names, tags=tags)

    def get_tags_by_name(self, tag_names):
        tags = self.get_tags()
        return tags_by_name(desired_tags=tag_names, tags=tags)