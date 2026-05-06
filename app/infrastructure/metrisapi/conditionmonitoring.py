from metrisapi.base import json_response, MetrisClient

class ConditionMonitoringSystemClient(MetrisClient):
    @json_response
    def get_report_sensors(self, reportid):
        uri = f'{self.base_uri}/api/conditionMonitoring/sensors/vibereport/{reportid}'
        return self.session.get(uri, headers=self._get_headers())		
    @json_response
    def get_sensor_measurements_basic_info(self, sensorId, start, end):
        uri = f'{self.base_uri}/api/conditionMonitoring/sensors/{sensorId}/measurementsbasic?start={start}&end={end}'
        return self.session.get(uri, headers=self._get_headers())		
    @json_response
    def get_processed_sensor_measurements_overview(self, sensorId, measurementId, start, end):
        uri = f'{self.base_uri}/api/conditionMonitoring/sensors/{sensorId}/{measurementId}/measurementsview?start={start}&end={end}'
        return self.session.get(uri, headers=self._get_headers())
    @json_response
    def get_processed_sensor_measurement_overview(self, sensorId, start, end):
        uri = f'{self.base_uri}/api/conditionMonitoring/sensors/{sensorId}/measurementview?start={start}&end={end}'
        return self.session.get(uri, headers=self._get_headers())