from django.db import models
import os
import binascii
import datetime
from django.conf import settings
 
def random_password():
    return binascii.b2a_qp(os.urandom(1024))

class PasswordXMLRPCServerProxy(models.Model):
    '''
    Implements a server proxy for XML-RPC calls that checks SSL certs and
    uses a password to talk to the server. The password is automatically renewed
    whenever it expires.
    '''
    
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=3072, default=random_password)
    max_password_age = models.IntegerField(
        'Max Password age (days)', default=60)
    password_timestamp = models.DateTimeField(auto_now_add=True)
    url = models.URLField("Server URL", max_length=1024,
                          verify_exists=False)
    
    verify_certs = models.BooleanField("Verify Certificates?", default=False)
    
    def __init__(self, *args, **kwargs):
        super(PasswordXMLRPCServerProxy, self).__init__(*args, **kwargs)
        self.transport = None
    
    def __getattr__(self, name):
        if name == "proxy":
            from xmlrpclib import ServerProxy
            from datetime import timedelta
            import time
            
            # TODO: re-enable SSL/safe transport
            if self.verify_certs:
                from clearinghouse.utils.transport import PyCURLSafeTransport as transport
                self.transport = transport(
                    timeout=settings.XMLRPC_TIMEOUT,
                    username=self.username,
                    password=self.password,
                    ca_cert_path=settings.XMLRPC_TRUSTED_CA_PATH)
            else:
                from clearinghouse.utils.transport import PyCURLSafeTransport as transport
                self.transport = transport(
                    timeout=settings.XMLRPC_TIMEOUT,
                    username=self.username,
                    password=self.password)
            
            self.proxy = ServerProxy(self.url, self.transport)
            
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
        self.verify_certs = True
        if self.transport:
            self.transport.set_ssl_verify(settings.XMLRPC_TRUSTED_CA_PATH)
        
    def change_password(self, password=None):
        # TODO: Fix
        return ""
#        password = password or random_password()
#        self.password_timestamp = datetime.date.today()
#        retval = self.__getattr__('change_password')(password)
#        self.password = password
#        del self.proxy
#        self.save()
#        return retval
        
    def is_available(self):
        '''Call the server's ping method, and see if we get a pong'''
        try:
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
        import urlparse
        import subprocess
        
        # parse the url
        res = urlparse.urlparse(self.url)
        port = res.port or 443
        
        # get the PEM-encoded certificate
        cert = ssl.get_server_certificate((res.hostname, port))
        
        # the returned cert maybe messed up because python's ssl is crap. Fix it
        if not cert.endswith("\n-----END CERTIFICATE-----\n"):
            cert.replace("-----END CERTIFICATE-----\n",
                         "\n-----END CERTIFICATE-----\n")
        
        # dump it in the directory, and run make
        with open(os.path.join(settings.XMLRPC_TRUSTED_CA_PATH,
                               res.hostname+"-ca.crt"),
                 'w') as cert_file:
            cert_file.write(cert)
        
        subprocess.call(['make', '-C', settings.XMLRPC_TRUSTED_CA_PATH])
