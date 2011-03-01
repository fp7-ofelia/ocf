'''
@author: jnaous
'''

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
import xmlrpclib
import urlparse
import base64
import logging

logger = logging.getLogger("TestClientTransport")

class AuthorizationRequired(Exception):
    pass

class TestClientTransport(xmlrpclib.Transport):
    """Handles connections to XML-RPC server through Django test client"""
    
    def __init__(self, defaults={}, *args, **kwargs):
        from django.test.client import Client
        xmlrpclib.Transport.__init__(self, *args, **kwargs)
        self.client = Client(**defaults)

    def add_auth(self, host, headers):
        """
        Add Basic authentication information to the headers if it is given
        in host.
        """
        url = "http://%s" % host
        parsed = urlparse.urlparse(url)
        if parsed.username and parsed.password:
            auth = "%s:%s" % (parsed.username, parsed.password)
            headers["HTTP_AUTHORIZATION"] = "Basic %s" % base64.b64encode(auth)

    def request(self, host, handler, request_body, verbose=0):
        headers = dict(content_type="text/xml")
        self.add_auth(host, headers)
        self.verbose = verbose
        response = self.client.post(handler, request_body, **headers)
        logger.debug("Received response:\n%s" % response)
        if "WWW-Authenticate" in response:
            raise AuthorizationRequired(
                "Authorization required. Got response\n%s" % response)
        res = StringIO(response.content)
        res.seek(0)
        return self.parse_response(res)
