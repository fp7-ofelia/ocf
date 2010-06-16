'''
@author: jnaous
'''

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
import xmlrpclib

class TestClientTransport(xmlrpclib.Transport):
    """Handles connections to XML-RPC server through Django test client"""
    
    def __init__(self, *args, **kwargs):
        from django.test.client import Client
        self.client = Client()

    def request(self, host, handler, request_body, verbose=0):
        self.verbose = verbose
        response = self.client.post(handler,
                                    request_body,
                                    content_type="text/xml")
        res = StringIO(response.content)
        res.seek(0)
        return self.parse_response(res)
