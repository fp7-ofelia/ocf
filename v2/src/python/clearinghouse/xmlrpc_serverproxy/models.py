from django.db import models
import os
import binascii

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
    password_timestamp = models.DateField(auto_now_add=True)
    url = models.URLField("Server URL", max_length=1024,
                          verify_exists=False)
    
    verify_ca = models.BooleanField("Verify CA?", default=True)
        
    def __getattr__(self, name):
        if name == "proxy":
            from xmlrpclib import ServerProxy
            from clearinghouse.utils import PyCURLSafeTransport
            from django.conf import settings
            from datetime import timedelta, date
            
            if self.verify_ca:
                self.proxy = ServerProxy(
                    self.url, PyCURLSafeTransport(
                        timeout=settings.XMLRPC_TIMEOUT,
                        username=self.username,
                        password=self.password,
                        ca_cert_path=settings.XMLRPC_TRUSTED_CA_PATH))
            else:
                self.proxy = ServerProxy(
                    self.url, PyCURLSafeTransport(
                        timeout=settings.XMLRPC_TIMEOUT,
                        username=self.username,
                        password=self.password,
                    ))
            
            # if the password has expired, it's time to set a new one
            max_age = timedelta(days=self.max_password_age)
            if self.password_timestamp + max_age >= date.today():
                self.change_password(random_password())
                
            return self.proxy
        else:
            return getattr(self.proxy, name)
        
    def change_password(self, password=None):
        password = password or random_password()
        self.proxy.change_password(password)
        self.password = password
        
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
        from django.conf import settings
        
        # parse the url
        res = urlparse.urlparse(self.url)
        port = res.port or 443
        
        # get the PEM-encoded certificate
        cert = ssl.get_server_certificate((res.hostname, port))
        
        # dump it in the directory, and run make
        with open(os.path.join(settings.XMLRPC_TRUSTED_CA_PATH,
                               res.hostname+".ca.cert"),
                 'w') as cert_file:
            cert_file.write(cert)
        
        subprocess.call(['make', '-C', settings.XMLRPC_TRUSTED_CA_PATH])
