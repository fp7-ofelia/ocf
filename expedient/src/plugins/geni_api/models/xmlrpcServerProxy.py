"""
Implements a server proxy for XML-RPC calls that checks SSL certs and
uses a password to talk to the server. The password is automatically renewed
whenever it expires.

@date: Apr 29, 2010
@author: jnaous
"""

from django.db import models

class xmlrpcServerProxy(models.Model):

    class Meta:
        app_label = 'geni_api'

    #api_version = models.CharField(max_length=30)
    #rspec_version = models.CharField(max_length=30)
    #uuid = models.CharField(max_length=36)
    #urn = models.CharField(max_length=256)
    #gid = models.TextField("GID") 
    url = models.URLField("Server URL", verify_exists = False, max_length=1024,
         help_text="URL used to access the remote server's xmlrpc interface, should be https://DOMAIN_OR_IP:PORT/ROUTE_TO_XMLRPC_INTERFACE")
