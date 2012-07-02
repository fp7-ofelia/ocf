'''
Views Tests
-------------------------

'''

import unittest
import xmlrpclib
from expedient.common.rpc4django.jsonrpcdispatcher import json, JSONRPC_SERVICE_ERROR
from expedient.common.rpc4django import views
from expedient.common.tests.manager import SettingsTestCase
from django.core.urlresolvers import reverse

class TestRPCViews(SettingsTestCase):

    urls = "expedient.common.rpc4django.tests.test_urls"
    
    def setUp(self):
        self.settings_manager.set(
            INSTALLED_APPS=(
                "expedient.common.rpc4django",
                "expedient.common.rpc4django.tests.testmod",
            ),
            MIDDLEWARE_CLASSES=(
                'django.middleware.common.CommonMiddleware',
                'django.middleware.transaction.TransactionMiddleware',
                'django.middleware.csrf.CsrfViewMiddleware',
                'django.contrib.sessions.middleware.SessionMiddleware',
                'django.contrib.auth.middleware.AuthenticationMiddleware',
            ),
            DEBUG_PROPAGATE_EXCEPTIONS=False,
        )
        
        views._register_rpcmethods(
            [
                "expedient.common.rpc4django",
                "expedient.common.rpc4django.tests.testmod",
            ],
            restrict_introspection=False,
            dispatchers=views.dispatchers)
        
        self.rpc_path = reverse("serve_rpc_request")
        self.ns_rpc_path = reverse("my_url_name")
        
    def test_methodsummary(self):
        response = self.client.get(self.rpc_path)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template.name, 'rpc4django/rpcmethod_summary.html')
    
    def test_xmlrequests(self):
        data = '<?xml version="1.0"?><methodCall><methodName>system.listMethods</methodName><params></params></methodCall>'
        response = self.client.post(self.rpc_path, data, 'text/xml')
        self.assertEqual(response.status_code, 200)
        xmlrpclib.loads(response.content)       # this will throw an exception with bad data
        
    def test_jsonrequests(self):
        data = '{"params":[],"method":"system.listMethods","id":123}'
        response = self.client.post(self.rpc_path, data, 'application/json')
        self.assertEqual(response.status_code, 200)
        jsondict = json.loads(response.content)
        self.assertTrue(jsondict['error'] is None)
        self.assertEqual(jsondict['id'], 123)
        self.assertTrue(isinstance(jsondict['result'], list))
        
        data = '{"params":[],"method":"system.describe","id":456}'
        response = self.client.post(self.rpc_path, data, 'text/javascript')
        self.assertEqual(response.status_code, 200)
        jsondict = json.loads(response.content)
        self.assertTrue(jsondict['error'] is None)
        self.assertEqual(jsondict['id'], 456)
        self.assertTrue(isinstance(jsondict['result'], dict))
        
    def test_typedetection(self):
        data = '{"params":[],"method":"system.listMethods","id":123}'
        response = self.client.post(self.rpc_path, data, 'text/plain')
        self.assertEqual(response.status_code, 200)
        jsondict = json.loads(response.content)
        self.assertTrue(jsondict['error'] is None)
        self.assertEqual(jsondict['id'], 123)
        self.assertTrue(isinstance(jsondict['result'], list))
        
        data = '<?xml version="1.0"?><methodCall><methodName>system.listMethods</methodName><params></params></methodCall>'
        response = self.client.post(self.rpc_path, data, 'text/plain')
        self.assertEqual(response.status_code, 200)
        xmlrpclib.loads(response.content)       # this will throw an exception with bad data
        
        # jsonrpc request with xmlrpc data (should be error)
        data = '<?xml version="1.0"?><methodCall><methodName>system.listMethods</methodName><params></params></methodCall>'
        response = self.client.post(self.rpc_path, data, 'application/json')
        self.assertEqual(response.status_code, 200)
        jsondict = json.loads(response.content)
        self.assertTrue(jsondict['result'] is None)
        self.assertEqual(jsondict['id'], '')
        self.assertTrue(isinstance(jsondict['error'], dict))
        
        data = '{"params":[],"method":"system.listMethods","id":123}'
        try:
            response = self.client.post(self.rpc_path, data, 'text/xml')
        except:
            # for some reason, this throws an expat error
            # but only in python 2.4
            return
        self.assertEqual(response.status_code, 200)
        try:
            xmlrpclib.loads(response.content)
            self.fail('parse error expected')
        except xmlrpclib.Fault:
            pass
        
    def test_badrequests(self):
        data = '{"params":[],"method":"system.methodHelp","id":456}'
        response = self.client.post(self.rpc_path, data, 'application/json')
        self.assertEqual(response.status_code, 200)
        jsondict = json.loads(response.content)
        self.assertTrue(jsondict['error'] is not None)
        self.assertEqual(jsondict['id'], 456)
        self.assertTrue(jsondict['result'] is None)
        self.assertEqual(jsondict['error']['code'], JSONRPC_SERVICE_ERROR)
        
        data = '<?xml version="1.0"?><methodCall><methodName>method.N0t.Exists</methodName><params></params></methodCall>'
        response = self.client.post(self.rpc_path, data, 'text/xml')
        self.assertEqual(response.status_code, 200)
        try:
            xmlrpclib.loads(response.content)
            self.fail('parse error expected')
        except xmlrpclib.Fault, fault:
            self.assertEqual(fault.faultCode, 1)
        
    def test_httpaccesscontrol(self):
        import django
        t = django.VERSION
        
        if t[0] < 1 or (t[0] == 1 and t[1] < 1):
            # options requests can only be tested by django 1.1+
            self.fail('This version of django "%s" does not support http access control' %str(t))
        
        response = self.client.options(self.rpc_path, '', 'text/plain')
        self.assertEqual(response['Access-Control-Allow-Methods'], 'POST, GET, OPTIONS')
        self.assertEqual(response['Access-Control-Max-Age'], '0')
        
    def test_good_url_name(self):
        """
        Make sure we call functions based on the url they are arriving on. 
        """
        data = xmlrpclib.dumps((5, 4), "subtract")
        response = self.client.post(self.rpc_path, data, 'text/xml')
        self.assertEqual(response.status_code, 200)
        result, methname = xmlrpclib.loads(response.content)
        self.assertEqual(result, (1,))
        self.assertEqual(methname, None)
        
        data = xmlrpclib.dumps((5, 4), "product")
        response = self.client.post(self.ns_rpc_path, data, 'text/xml')
        self.assertEqual(response.status_code, 200)
        result, methname = xmlrpclib.loads(response.content)
        self.assertEqual(result, (20,))
        self.assertEqual(methname, None)

    def test_bad_url_name(self):
        """
        Make sure we cannot call functions using the wrong url_name.
        """
        data = xmlrpclib.dumps((5, 4), "subtract")
        response = self.client.post(self.ns_rpc_path, data, 'text/xml')
        
        self.assertEqual(response.status_code, 200)
        try:
            result, methname = xmlrpclib.loads(response.content)
            self.fail("Expected xmlrpclib Fault")
        except xmlrpclib.Fault as fault:
            self.assertEqual(fault.faultCode, 1)
            self.assertTrue(fault.faultString.endswith('method "subtract" is not supported'))
        
if __name__ == '__main__':
    unittest.main()