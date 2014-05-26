import xmlrpclib

"""
author: msune, CarolinaFernandez

Wrapper to create simple clients for GENI-based AMs (e.g. AMsoil).
"""

class SafeTransportWithCert(xmlrpclib.SafeTransport):
    """Helper class to foist the right certificate for the transport class."""
    def __init__(self, key_path, cert_path):
        xmlrpclib.SafeTransport.__init__(self) # no super, because old style class
        self._key_path = key_path
        self._cert_path = cert_path
    
    def make_connection(self, host):
        """This method will automatically be called by the ServerProxy class when a transport channel is needed."""
        host_with_cert = (host, {'key_file' : self._key_path, 'cert_file' : self._cert_path})
        return xmlrpclib.SafeTransport.make_connection(self, host_with_cert) # no super, because old style class

class GENIClient(object):
    def __init__(self, host, port, key_path=None, cert_path=None):
        """
        Establishes a connection proxy with the client certificate given.
        {host} e.g. 127.0.0.1
        {port} e.g. 8001
        {key_path} The file path to the client's private key.
        {cert_path} The file path to the client's certificate.
        """
        if not key_path and not cert_path:
            key_path = "/etc/apache2/ssl.key/server.key"
            cert_path = "/etc/apache2/ssl.crt/server.crt"
        
        transport = SafeTransportWithCert(key_path, cert_path)
        self._proxy = xmlrpclib.ServerProxy("https://%s:%s/RPC2" % (host, str(port)), transport=transport)
    
    def call_method(self, method_name, *params):
        """
        Calls to the method defined by the string passed as an argument.
        Raises exception if method not available.
        """
        try:
            return getattr(self._proxy, method_name)()
        except Exception as e:
            print "GENI Client error: %s" % str(e)
            raise e
