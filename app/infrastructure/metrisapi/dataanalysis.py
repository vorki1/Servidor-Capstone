from metrisapi.base import json_response, MetrisClient


class DataAnalysisClient(MetrisClient):
    @json_response
    def get_tag_lists(self):
        uri = f'{self.base_uri}/api/dataanalysis/taglists'
        return self.session.get(uri, headers=self._get_headers())

    @json_response
    def get_tag_list(self, id):
        uri = f'{self.base_uri}/api/dataanalysis/taglist/{id}'
        return self.session.get(uri, headers=self._get_headers())

    def get_tag_list_by_name(self, name):
        tag_lists = self.get_tag_lists() 
        tag_list_id = [i['id'] for i in tag_lists if i['name']==name][0]
        return self.get_tag_list(tag_list_id)
        
    @json_response
    def post_data_analysis(self, tagId, trend_values, id_row=None):
        # elem = {'timestamp': data[0][i].isoformat(),
        #         'value': float(data[1][i]),
        #         'editedBy': 1,
        #         'editedTimestamp': dt}
        
        # if id_row is specified, row will be modified and not changed
        if not id is None:
            trend_values['id'] = id_row
        
        uri = f'{self.base_uri}/api/dataanalysis'
        qparams = {'tagId': tagId}
        return self.session.post(uri, headers=self._get_headers(), params=qparams, data=trend_values)
