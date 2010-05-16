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
        
        call_env_command(test_settings.OM_PROJECT_DIR, "flush",
                         interactive=False)
        self.om_env = Env(test_settings.OM_PROJECT_DIR)
        self.om_env.switch_to()
        
        from optin_manager.dummyfv.models import DummyFV
        from django.contrib.auth.models import User
        
        # Create the clearinghouse user
        username = "clearinghouse"
        password = "password"
        u = User.objects.create(username=username)
        u.set_password(password)
        
        self.om_client = xmlrpclib.ServerProxy(
            "https://%s:%s@%s:%s/xmlrpc/xmlrpc/" % (
                username, password, test_settings.HOST, test_settings.PORT
            )
        )
        
        # Create dummy FVs
        for i in range(test_settings.NUM_DUMMY_FVS):
            fv = DummyFV.objects.create()
            # Load up a fake topology in the Dummy FV
            fv.populateTopology(10, 20, use_random=test_settings.USE_RANDOM)
            
            # TODO: Create the FV proxy connection
        
        
    def test_ping(self):
        """
        Communications are up.
        """
        ret = self.om_client.ping("PING")
        self.assertEqual(ret, "PONG: PING", "Ping returned %s." % ret)
        
    def test_get_switches(self):
        """
        Test that a slice can be created and the calls are routed to the
        FV correctly.
        """
        from optin_manager.dummyfv.models import DummyFVDevice
        from optin_manager.flowspace.utils import long_to_dpid, dpid_to_long

        # TODO: Fix to also check the returned info
        dpids_info = self.om_client.get_switches()
        dpids = set([d[0] for d in dpids_info])
        
        # check that we expect all the dpids
        expected = set(
            map(
                dpid_to_long,
                DummyFVDevice.objects.values_list('dpid', flat=True),
            )
        )
        
        self.assertEqual(
            dpids, expected, 
            "Received dpids (%s) not same as expected (%s)." % (
                dpids, expected,
            )
        )
        
    def test_get_links(self):
        """
        Tests that the links are retrieved correctly from the FV.
        """
        from optin_manager.dummyfv.models import DummyFVLink
        from optin_manager.flowspace.utils import long_to_dpid, dpid_to_long

        links = set(self.om_client.get_links())
        
        expected = set([(
            dpid_to_long(link.dst_dev.dpid),
            link.dst_port,
            dpid_to_long(link.src_dev.dpid),
            link.src_port, {}) for link in DummyFVLink.objects.all()])
        
        self.assertEqual(
            links, expected,
            "Received links (%s) not same as expected (%s)" % (
                links, expected,
            )
        )
        
    def test_change_password(self):
        # TODO: write up test_change_password
        pass
    
    def test_topology_callback(self):
        # TODO: write up test_topology_callback
        pass
    
    def test_create_slice(self):
        # TODO: write up test_create_slice
        pass
    
    def test_delete_slice(self):
        # TODO: write up test_delete_slice
        pass
        
if __name__ == '__main__':
    import unittest
    unittest.main()
