from django.db import models

class xmlrpcServerProxy(models.Model):
    '''
    Implements a server proxy for XML-RPC calls that checks SSL certs and
    uses a password to talk to the server. The password is automatically renewed
    whenever it expires.
    '''
    
    class Meta:
        app_label = 'sample_resource'
    
    username = models.CharField(
        max_length=100,
        help_text="Username to use to access the remote server.")
    password = models.CharField(
        max_length=24,
        help_text="Password to use to access the remote server.")
    url = models.URLField("Server URL", verify_exists = False, max_length=1024,
         help_text="URL used to access the remote server's xmlrpc interface, should be https://DOMAIN_OR_IP:PORT/ROUTE_TO_XMLRPC_INTERFACE")
