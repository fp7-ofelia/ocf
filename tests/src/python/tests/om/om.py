'''
Created on May 15, 2010

@author: jnaous
'''

from unittest import TestCase
from tests.commands import call_env_command, Env
import test_settings
import xmlrpclib

class OMTests(TestCase):
    
    def setUp(self):
        """
        Load up a DB for the OM.
        Create a client to talk to the OM.
        """
        
        call_env_command(test_settings.OM_PROJECT_DIR, "flush", interactive=False)
        self.om_env = Env(test_settings.OM_PROJECT_DIR)
        self.om_env.switch_to()
        
        # Create the clearinghouse user
        from django.contrib.auth.models import User
        username = "clearinghouse"
        password = "password"
        u = User.objects.create(username=username)
        u.set_password(password)
        
        self.om_client = xmlrpclib.ServerProxy(
            "https://%s:%s@%s:%s/xmlrpc/xmlrpc/" % (
                username, password, test_settings.HOST, test_settings.PORT
            )
        )
        
    def test_ping(self):
        """
        Communications are up.
        """
        ret = self.om_client.ping("PING")
        self.assertEqual(ret, "PONG: PING", "Ping returned %s." % ret)
        