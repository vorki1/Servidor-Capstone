from metrisapi.base import json_response, MetrisClient


class LogBookUpdatesParameters:
    def __init__(self, since : str, max_count = None, only_posts_by_user = False):
        self.since = since
        self.max_count = max_count
        self.only_posts_by_user = only_posts_by_user
        
    def as_querystring_dictionary(self):
        return {
            'since': self.since,
            'maxcount': self.max_count,
            'onlypostsbyuser': self.only_posts_by_user,
        }
        
        
class LogBookClient(MetrisClient):
    
    @json_response
    def get_logbook_updates(self, logbook_updates_parameters):
        uri = f'{self.base_uri}/api/logbook/updates'
        params = logbook_updates_parameters.as_querystring_dictionary()
        return self.session.get(uri, headers=self._get_headers(), params=params)
        
    @json_response
    def get_logbook_note(self, note_id : int):
        uri = f'{self.base_uri}/api/logbook/notes/{note_id}'
        return self.session.get(uri, headers=self._get_headers())
        