import argparse
import unittest
from unittest.mock import patch, Mock

import agent
import api_client
from app import app


class Tests(unittest.TestCase):
    def test_gateway_service_error_retains_code(self):
        response = Mock(ok=False, status_code=400, json=lambda: {'OpenAPI_ServiceResponse': {'cmmMsgHeader': {'returnReasonCode': '12', 'returnAuthMsg': 'secret-marker'}}})
        with patch.dict('os.environ', {'SERVICE_KEY':'test'}), patch('api_client.requests.get', return_value=response):
            with self.assertRaises(api_client.APIError) as error:
                api_client.get('GetCtyCodeList')
            self.assertEqual(error.exception.info['api_code'], '12')
            self.assertNotIn('secret-marker', str(error.exception.info))

    def test_invalid_input_never_calls_api(self):
        with patch('app.get') as get:
            response = app.test_client().get('/search?departure=X&arrival=X&date=2000-01-01')
            self.assertEqual(response.status_code, 400)
            get.assert_not_called()

    def test_secret_not_in_network_error(self):
        with patch.dict('os.environ', {'SERVICE_KEY': 'secret-marker'}), patch('api_client.requests.get', side_effect=api_client.requests.ConnectionError('secret-marker')):
            with self.assertRaises(api_client.APIError) as error:
                api_client.get('GetCtyCodeList')
            self.assertNotIn('secret-marker', str(error.exception.info))

    def test_pagination_and_single_item(self):
        def response(items):
            return Mock(ok=True, status_code=200, json=lambda: {'response': {'header': {'resultCode':'00'}, 'body': {'items': {'item':items}, 'totalCount':2}}})
        with patch.dict('os.environ', {'SERVICE_KEY':'test'}), patch('api_client.requests.get', side_effect=[response({'id':1}), response([{'id':2}])]) as get:
            self.assertEqual(len(api_client.get('GetCtyCodeList')), 2)
            self.assertEqual(get.call_count, 2)

    def test_auth_xml(self):
        response = Mock(ok=True, status_code=200, text='<OpenAPI_ServiceResponse><cmmMsgHeader><returnReasonCode>30</returnReasonCode></cmmMsgHeader></OpenAPI_ServiceResponse>')
        response.json.side_effect = ValueError()
        with patch.dict('os.environ', {'SERVICE_KEY':'test'}), patch('api_client.requests.get', return_value=response):
            with self.assertRaises(api_client.APIError) as error:
                api_client.get('GetCtyCodeList')
            self.assertEqual(error.exception.info['kind'], 'AUTH_ERROR')

    def test_agent_retries_once_and_does_not_retry_auth(self):
        args = argparse.Namespace(departure='A', arrival='B', date='2099-01-01', start_time='00:00', end_time='23:59', train_type='', city_code='11', recover=True)
        for kind, calls in [('NETWORK_ERROR', 2), ('AUTH_ERROR', 1)]:
            action = Mock(side_effect=api_client.APIError(kind, 'safe error'))
            with patch('agent.prerequisites', return_value={'missing_files':[], 'missing_packages':[], 'env_exists':True}), patch('agent.local_health', return_value={'pid':1}), patch('agent.port_open', return_value=True), patch('agent.dns', return_value='OK'), patch('agent.base_url', return_value='OK'), patch('agent.api_probes', return_value={'CITY_API':action}):
                self.assertEqual(agent.run(args)['status'], 'ERROR')
                self.assertEqual(action.call_count, calls)

    def test_filter_and_six_columns(self):
        row = dict(depplandtime=20990101090000, arrplandtime=20990101100000, traingradename='KTX', trainno=1, depplacename='서울', arrplacename='대전')
        with patch('app.get', return_value=[row]):
            client = app.test_client()
            response = client.get('/search?departure=A&arrival=B&date=2099-01-01&start_time=09:00&end_time=09:00')
            self.assertEqual(len(response.json['items'][0]), 6)
            response = client.get('/search?departure=A&arrival=B&date=2099-01-01&start_time=10:00&end_time=11:00')
            self.assertEqual(response.json['status'], 'NO_DATA')

    def test_recovery_verifies_screen_and_reports_recovered(self):
        args = argparse.Namespace(departure='A', arrival='B', date='2099-01-01', start_time='00:00', end_time='23:59', train_type='', city_code='11', recover=True)
        action = Mock(side_effect=[api_client.APIError('NETWORK_ERROR', 'temporary'), [{'id': 1}]])
        with patch('agent.prerequisites', return_value={'missing_files':[], 'missing_packages':[], 'env_exists':True}), patch('agent.local_health', return_value={'pid':1}), patch('agent.port_open', return_value=True), patch('agent.dns', return_value='OK'), patch('agent.base_url', return_value='OK'), patch('agent.api_probes', return_value={'CITY_API':action}), patch('agent.screen_probe', return_value='OK') as screen:
            result = agent.run(args)
            self.assertEqual(result['status'], 'RECOVERED')
            self.assertEqual(action.call_count, 2)
            self.assertEqual(screen.call_count, 5)


if __name__ == '__main__':
    unittest.main()
