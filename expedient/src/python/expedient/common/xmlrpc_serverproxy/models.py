'''
Created on Apr 30, 2010

@author: jnaous
'''

from django.db import models
import os
import binascii
from django.conf import settings
from datetime import timedelta, datetime
import time
from expedient.common.utils.transport import TestClientTransport
from urlparse import urlparse
from django.contrib.auth.models import User
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

class PasswordXMLRPCServerProxy(models.Model):
    '''
    Implements a server proxy for XML-RPC calls that checks SSL certs and
    uses a password to talk to the server. The password is automatically renewed
    whenever it expires.
    '''
    
    username = models.CharField(
        max_length=100,
        help_text="Username to use to access the remote server.")
    password = models.CharField(
        max_length=get_max_password_len(),
        help_text="Password to use to access the remote server.")
    max_password_age = models.PositiveIntegerField(
        'Max Password age (days)', default=0,
        help_text="If this is set to non-zero, the password "\
            "will automatically be changed once the password ages past the "\
            "maximum. The new password is then randomly generated.")
    password_timestamp = models.DateTimeField(auto_now_add=True)
    url = models.CharField("Server URL", max_length=1024, help_text="URL used to access the remote server's xmlrpc interface, should be https://DOMAIN_OR_IP:PORT/ROUTE_TO_XMLRPC_INTERFACE")
    
    verify_certs = models.BooleanField(
        "Verify Certificates?", default=False,
        help_text="Disabling this check will still verify that the "\
            "certificate itself is well-formed. In particular, the "\
            "server's hostname must match the certificate's Common Name.")
    
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
                                              transport=self.transport,
                                              #verbose=getattr(settings, "DEBUG", False))
                                              verbose=False)
            self.set_verify_certs()
        else:
            self.proxy = BasicAuthServerProxy(self.url,
                                              username=self.username,
                                              password=self.password)
    
    def _check_expiry(self):
        # if the password has expired, it's time to set a new one
        if self.password_timestamp and self.max_password_age:
            max_age = timedelta(days=self.max_password_age)
            expiry_time = self.password_timestamp + max_age
            # normalize because django is screwy
            expiry_time = time.mktime(expiry_time.timetuple())
            now = time.time()
            if expiry_time <= now:
                self.proxy.change_password(random_password())
                
    def __init__(self, *args, **kwargs):
        super(PasswordXMLRPCServerProxy, self).__init__(*args, **kwargs)
        if self.url:
            self._reset_proxy()
        self._check_expiry()
    
#    def __getattr__(self, name):
#        if name == "proxy":
#            raise AttributeError("Attribute 'proxy' not found.")
#        return getattr(self.proxy, name)
        
    def save(self, *args, **kwargs):
        super(PasswordXMLRPCServerProxy, self).save(*args, **kwargs)
        if self.url:
            self._reset_proxy()
            self.set_verify_certs()
        
    def set_verify_certs(self):
        '''Enable/disable SSL certificate verification.'''
        if self.transport:
            from M2Crypto import SSL
            if self.verify_certs:
                self.transport.ssl_ctx.set_verify(
                    SSL.verify_peer | SSL.verify_fail_if_no_peer_cert, 16)
                self.transport.ssl_ctx.load_verify_locations(
                    capath=settings.XMLRPC_TRUSTED_CA_PATH)
            else:
                self.transport.ssl_ctx.set_verify(
                    SSL.verify_none, 1)
            
    def change_password(self, password=None):
        '''Change the remote password'''
        password = password or random_password()
        self.password_timestamp = datetime.today()
        err = self.__getattr__('change_password')(password)
        if not err:
            # password change succeeded
            self.password = password
            self._reset_proxy()
            self.save()
        else:
            print "Error changing password: %s" % err
        return err
        
    def ping(self, data):
        return self.proxy.ping(data)
        
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
        with open(os.path.join(settings.XMLRPC_TRUSTED_CA_PATH,
                               res.hostname+"-ca.crt"),
                 'w') as cert_file:
            cert_file.write(cert)
        
        # TODO: Don't run make here. Do the linking manually.
        subprocess.Popen(['make', '-C', settings.XMLRPC_TRUSTED_CA_PATH],
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         )
