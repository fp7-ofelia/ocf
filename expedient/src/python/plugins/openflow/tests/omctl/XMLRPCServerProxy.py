'''
NOTE: This is the same code as expedient.common.xmlrpc_serverproxy 
with some changes to make it independent from Django Models.model
so that it can be used independently.
'''

import os
import binascii
from omctl_settings import *
from datetime import timedelta, datetime
import time
from expedient.common.utils.transport import TestClientTransport
from urlparse import urlparse
import xmlrpclib
from expedient.common.tests.utils import test_to_http

def get_max_password_len():
    # M2Crypto does not like it when header fields are large. Creates bad
    # requests. So limit to 40 hex characters = 20 bytes = 160 bits.
    return 40

def random_password():
    return binascii.b2a_hex(os.urandom(get_max_password_len()/2))

def add_basic_auth(uri, username=None, password=None):
    parsed = urlparse(uri.lower())
    if username:
        if password:
            new_url = "%s://%s:%s@%s%s" % (parsed.scheme,
                                           username,
                                           password,
                                           parsed.netloc,
                                           parsed.path)
        else:
            new_url = "%s://%s@%s%s" % (parsed.scheme,
                                        username,
                                        parsed.netloc,
                                        parsed.path)
    else:
        new_url = uri
    return new_url

class BasicAuthServerProxy(xmlrpclib.ServerProxy):
    def __init__(self, uri, username=None, password=None, **kwargs):
        new_url = add_basic_auth(uri, username, password)
        
        # M2Crypto fails when using unicode URLs.
        xmlrpclib.ServerProxy.__init__(self, str(new_url), **kwargs)

    def __repr__(self):
        parsed = urlparse(self._ServerProxy__host)
        new_url = "%s://%s%s" % (parsed.scheme,
                                 parsed.netloc,
                                 parsed.path)
        return (
            "<ServerProxy for %s%s>" %
            (new_url, self._ServerProxy__handler)
            )

    __str__ = __repr__

class PasswordXMLRPCServerProxy: 
    def setup(self, username, password, url, verify_certs=True):
        self.username = username
        self.password = password
        self.url = url
        self.verify_certs = verify_certs
        if self.url:
            self._reset_proxy()
            self.set_verify_certs()
               
    def _reset_proxy(self):
        parsed = urlparse(self.url.lower())
        self.transport = None
        # This scheme is used for debugging and looping back
        if parsed.scheme == "test":
            self.proxy = BasicAuthServerProxy(
                test_to_http(self.url),
                username=self.username,
                password=self.password,
                transport=TestClientTransport())
        elif parsed.scheme == "https":
            from M2Crypto.m2xmlrpclib import SSL_Transport
            from M2Crypto.SSL import Context
            self.transport = SSL_Transport(Context(protocol='tlsv1'))
            self.proxy = BasicAuthServerProxy(self.url,
                                              username=self.username,
                                              password=self.password,
                                              transport=self.transport)
            self.set_verify_certs()
        else:
            self.proxy = BasicAuthServerProxy(self.url,
                                              username=self.username,
                                              password=self.password)          
    
    def __getattr__(self, name):
        if name == "proxy":
            raise AttributeError("Attribute 'proxy' not found.")
        return getattr(self.proxy, name)
        

        
    def set_verify_certs(self):
        '''Enable/disable SSL certificate verification.'''
        if self.transport:
            from M2Crypto import SSL
            if self.verify_certs:
                self.transport.ssl_ctx.set_verify(
                    SSL.verify_peer | SSL.verify_fail_if_no_peer_cert, 16)
                self.transport.ssl_ctx.load_verify_locations(
                    capath=XMLRPC_TRUSTED_CA_PATH)
            else:
                self.transport.ssl_ctx.set_verify(
                    SSL.verify_none, 1)
            
    def change_password(self, password=None):
        '''Change the remote password'''
        password = password or random_password()
        err = self.__getattr__('change_password')(password)
        if not err:
            # password change succeeded
            self.password = password
            self._reset_proxy()
        else:
            print "Error changing password: %s" % err
        return err
        
    def is_available(self, get_info=False):
        '''Call the server's ping method, and see if we get a pong'''
        try:
            ret = self.ping("PING")
        except Exception as e:
            import traceback
            print "Exception while pinging server: %s" % e
            traceback.print_exc()
            if get_info:
                return (False, str(e))
            else:
                return False
            
        if "PING" in ret and "PONG" in ret:
            if get_info:
                return (True, None)
            else:
                return True
        else:
            msg = "Server at %s returned unexpected data %s" % (self.url, ret)
            print msg
            if get_info:
                return (False, msg)
            else:
                return False
        
    def install_trusted_ca(self):
        '''
        Add the CA that signed the certificate for self.url as trusted.
        '''
        import ssl
        import subprocess

        # parse the url
        res = urlparse(self.url)
        if res.scheme.lower() != "https":
            return
        
        port = res.port or 443
        
        # get the PEM-encoded certificate
        cert = ssl.get_server_certificate((res.hostname, port))
        
        # the returned cert maybe messed up because of python-ssl bug Issue8086
        if not cert.endswith("\n-----END CERTIFICATE-----\n"):
            cert = cert.replace("-----END CERTIFICATE-----",
                                "\n-----END CERTIFICATE-----\n")
        
        # dump it in the directory, and run make
        with open(os.path.join(XMLRPC_TRUSTED_CA_PATH,
                               res.hostname+"-ca.crt"),
                 'w') as cert_file:
            cert_file.write(cert)
        
        # TODO: Don't run make here. Do the linking manually.
        subprocess.Popen(['make', '-C', XMLRPC_TRUSTED_CA_PATH],
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         )
