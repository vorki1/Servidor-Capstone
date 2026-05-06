from metrisapi.base import json_response, MetrisClient

class ReportingClient(MetrisClient):
    @json_response
    def get_report_data(self, reportid, date):
        uri = f'{self.base_uri}/api/reporting/GetReportDataSource?reportId={reportid}&timestamp={date}'
        return self.session.get(uri, headers=self._get_headers())
    @json_response
    def get_report_template(self, reportid):
        uri = f'{self.base_uri}/api/reporting/GetReport/{reportid}'
        return self.session.get(uri, headers=self._get_headers())
    def get_report_sensor(self, reportid):
        uri = f'{self.base_uri}/api/reporting/getreportsensor/{reportid}'
        return self.session.get(uri, headers=self._get_headers())
    def upload_report_content(self, reportid, taskid, content):
        uri = f'{self.base_uri}/api/reporting/uploadreportcontent'
        qparams = {'reportId': reportid, 'taskid': taskid}
        return self.session.post(uri, headers={**self._get_headers(), 'Content-Type': 'application/json'}, params=qparams, data=content)
        