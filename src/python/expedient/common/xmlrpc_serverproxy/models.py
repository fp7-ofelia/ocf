'''
Created on Apr 30, 2010

@author: jnaous
'''

from django.db import models
import os
import binascii
from django.conf import settings
from xmlrpclib import ServerProxy
from datetime import timedelta, datetime
import time
from expedient.common.utils.transport import PyCURLSafeTransport as transport
from urlparse import urlparse
from django.contrib.auth.models import User

def get_max_password_len():
    return User._meta.get_field_by_name('password')[0].max_length

def random_password():
    return binascii.b2a_hex(os.urandom(get_max_password_len()/2))

class PasswordXMLRPCServerProxy(models.Model):
    '''
    Implements a server proxy for XML-RPC calls that checks SSL certs and
    uses a password to talk to the server. The password is automatically renewed
    whenever it expires.
    '''
    
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=get_max_password_len(),
                                default=random_password)
    max_password_age = models.IntegerField(
        'Max Password age (days)', default=60)
    password_timestamp = models.DateTimeField(auto_now_add=True)
    url = models.CharField("Server URL", max_length=1024)
    
    verify_certs = models.BooleanField("Verify Certificates?", default=False)
    
    def __init__(self, *args, **kwargs):
        super(PasswordXMLRPCServerProxy, self).__init__(*args, **kwargs)
        self.transport = None
    
    def __getattr__(self, name):
        if name == "proxy":
            if self.url.lower().startswith("https"):
                if self.verify_certs:
                    self.transport = transport(
                        timeout=settings.XMLRPC_TIMEOUT,
                        username=self.username,
                        password=self.password,
                        ca_cert_path=settings.XMLRPC_TRUSTED_CA_PATH)
                else:
                    self.transport = transport(
                        timeout=settings.XMLRPC_TIMEOUT,
                        username=self.username,
                        password=self.password)
                self.proxy = ServerProxy(self.url, self.transport)
            else:
                parsed = urlparse(self.url)
                new_url = "%s://%s:%s@%s%s" % (parsed.scheme,
                                               self.username,
                                               self.password,
                                               parsed.netloc,
                                               parsed.path)
                self.proxy =  ServerProxy(new_url)
            
            
            # if the password has expired, it's time to set a new one
            max_age = timedelta(days=self.max_password_age)
            expiry_time = self.password_timestamp + max_age
            # normalize because django is screwy
            expiry_time = time.mktime(expiry_time.timetuple())
            now = time.time()
            if expiry_time <= now:
                self.change_password(random_password())
                
            return self.proxy
        else:
            return getattr(self.proxy, name)
        
    def set_verify_certs(self, enable):
        '''Enable/disable SSL certificate verification.'''
        self.verify_certs = enable
        if self.transport:
            if enable:
                self.transport.set_ssl_verify(
                    ca_cert_path=settings.XMLRPC_TRUSTED_CA_PATH)
            else:
                self.transport.set_ssl_verify()
        
    def change_password(self, password=None):
        '''Change the remote password'''
        password = password or random_password()
        self.password_timestamp = datetime.today()
        err = self.__getattr__('change_password')(password)
        if not err:
            # password change succeeded
            self.password = password
            del self.proxy
            self.save()
        return err
        
    def is_available(self):
        '''Call the server's ping method, and see if we get a pong'''
        try:
            ret = self.ping("PING")
            if self.ping("PING") == "PONG: PING":
                return True
        except Exception, e:
            import traceback
            print "Exception while pinging server: %s" % e
            traceback.print_exc()
        return False

    def install_trusted_ca(self):
        '''
        Add the CA that signed the certificate for self.url as trusted.
        '''
        import ssl
        import subprocess

        # parse the url
        res = urlparse(self.url)
        port = res.port or 443
        
        # get the PEM-encoded certificate
        cert = ssl.get_server_certificate((res.hostname, port))
        
        # the returned cert maybe messed up because python's ssl is crap. Fix it
        if not cert.endswith("\n-----END CERTIFICATE-----\n"):
            cert = cert.replace("-----END CERTIFICATE-----",
                                "\n-----END CERTIFICATE-----\n")
        
        # dump it in the directory, and run make
        with open(os.path.join(settings.XMLRPC_TRUSTED_CA_PATH,
                               res.hostname+"-ca.crt"),
                 'w') as cert_file:
            cert_file.write(cert)
        
        subprocess.Popen(['make', '-C', settings.XMLRPC_TRUSTED_CA_PATH],
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         )
