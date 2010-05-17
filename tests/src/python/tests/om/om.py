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
        from optin_manager.xmlrpc_server.models import FVServerProxy
        
        # Create the clearinghouse user
        username = "clearinghouse"
        password = "password"
        u = User.objects.create(username=username)
        u.set_password(password)
        u.save()
        
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
            
            # create fake users for the Dummy FV
            username = "om%s" % i
            password = "password"
            u = User.objects.create(username=username)
            u.set_password(password)
            u.save()

            # Create the FV proxy connection
            FVServerProxy.objects.create(
                name="Flowvisor %s" % i,
                username=username,
                password=password,
                url = "https://%s:%s/dummyfv/%s/xmlrpc/",
            )
            
        
        
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
        self.dpids_info = self.om_client.get_switches()
        dpids = set([d[0] for d in self.dpids_info])
        
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
    
    def test_create_slice(self, id=10):
        """
        Tests that slices are created correctly from the OM to the FV
        """
        from tests.gapi.helpers import Flowspace
        from optin_manager.dummyfv.models import DummyFV, DummyFVRule
        from optin_manager.dummyfv.models import DummyFVSlice
        import random
        from optin_manager.flowspace.utils import dpid_to_long
        
        # get the switches into self.dpids_info
        self.test_get_switches()
        
        # create some random flowspaces
        switch_slivers=[]
        for i in xrange(10):
            switch = random.choice(self.dpids_info)
            fs_set = [Flowspace.create_random([switch]) \
                      for j in random.randint(1,10)]
            switch_slivers.append({
                "dapatapath_id": dpid_to_long(switch[0]),
                "flowspace": [fs.get_full_attrs() for fs in fs_set],
            })
        
        args = {
            "slice_id": id,
            "project_name": "project_name",
            "project_description": "project_description",
            "slice_name": "slice name %s" % id,
            "slice_description": "slice_description",
            "controller_url": "bla:bla.bla.bla:6633",
            "owner_email": "bla@bla.com",
            "owner_password": "password",
            "switch_slivers": switch_slivers,
        }
        
        # Create!
        ret = self.om_client.create_slice()
        
        # check the return value
        self.assertEqual(ret, {'error_msg': "", 'switches': []})
        
        for fv in DummyFV.objects.all():
            DummyFVSlice.objects.get(
                name=args["slice_name"],
                password=args["owner_password"],
                controller_url=args["controller_url"],
                email=args["owner_email"],
                fv=fv,
            )
            # TODO: Check that the rules are correct
            DummyFVRule.objects.print_rules(fv=fv)
            
    def test_delete_slice(self):
        """
        Tests that slices are deleted correctly from the OM to FV
        """
        import random
        from optin_manager.dummyfv.models import DummyFV, DummyFVSlice

        num_slices = random.randint(1, 5)
        for i in num_slices:
            self.test_create_slice(id=i)
        
        # delete some slices and make sure they are gone
        for i in random.shuffle(range(1, num_slices)):
            err = self.om_client.delete_slice(i)
            self.assertEqual(err == "")
            num_slices -= 1
            for fv in DummyFV.objects.all():
                num_actual_slices = DummyFVSlice.objects.filter(fv=fv).count()
                self.assertTrue(
                    num_actual_slices == num_slices,
                    "Expected %s slices after delete but found %s" % (
                        num_slices, num_actual_slices))
        
if __name__ == '__main__':
    import unittest
    unittest.main()
