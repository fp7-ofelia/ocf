'''
Created on May 11, 2010

@author: jnaous
'''
from unittest import TestCase
from tests.transport import SafeTransportWithCert
import xmlrpclib
from os.path import join
import test_settings as settings 
from helpers import parse_rspec, create_random_resv, kill_old_procs
from tests.commands import call_env_command, Env

class GAPITests(TestCase):
    """
    Test the GENI API interface. This assumes that Apache is currently running
    the clearinghouse over SSL. The clearinghouse will be contacting itself as
    the dummy Opt-in Managers. Assumes all certificates and keys in ssl dir.
    """

    def create_ch_slice(self):
        """
        Code mostly copied from GENI test harness from BBN.
        """
        import sfa.trust.credential as cred
        
        slice_cred_string = self.ch_client.CreateSlice()
        slice_credential = cred.Credential(string=slice_cred_string)
        slice_gid = slice_credential.get_gid_object()
        slice_urn = slice_gid.get_urn()
#        print 'Slice URN = %s' % (slice_urn)
        
        # Set up the array of credentials as just the slice credential
        credentials = [slice_cred_string]
        
        return (slice_urn, credentials)
        
    def setup_dummy_oms(self):
        from clearinghouse.dummyom.models import DummyOM
        from django.contrib.auth.models import User
        from clearinghouse.openflow.models import OpenFlowAggregate
        from clearinghouse.xmlrpc_serverproxy.models import PasswordXMLRPCServerProxy
        
        for i in range(settings.NUM_DUMMY_OMS):
            om = DummyOM.objects.create()
            om.populate_links(settings.NUM_SWITCHES_PER_AGG, 
                              settings.NUM_LINKS_PER_AGG)
            username = "clearinghouse%s" % i
            password = "clearinghouse"
            u = User.objects.create(username=username)
            u.set_password(password)
            u.save()
    
            # Add the aggregate to the CH
            proxy = PasswordXMLRPCServerProxy.objects.create(
                username=username,
                password=password,
                url="https://%s:%s/%sdummyom/%s/xmlrpc/" % (
                    settings.HOST, settings.PORT, settings.PREFIX, om.id,
                ),
                verify_certs = False,
            )
    
            # test availability
#            print "Checking availability."
            if not proxy.is_available:
                raise Exception("Problem: Proxy not available")
    
            # Add aggregate
            of_agg = OpenFlowAggregate.objects.create(
                name=username,
                description="hello",
                location="America",
                client=proxy,
            )
    
            err = of_agg.setup_new_aggregate(settings.HOST)
            if err:
                raise Exception("Error setting up aggregate: %s" % err)
        
    def setUp(self):
        """
        Load the DB fixtures for the AM (running using Apache).
        Create an xml-rpc client to talk to the AM Proxy through GAPI.
        Run the test clearinghouse, and create client to talk to it.
        """
#        print "Doing Setup"
        
        import shlex, subprocess, time
        
        call_env_command(settings.CH_PROJECT_DIR, "flush", interactive=False)
        
        self.ch_env = Env(settings.CH_PROJECT_DIR)
        self.ch_env.switch_to()
        
        self.setup_dummy_oms()
        
        # Create the ssl certificates if needed
        cmd = "make -C %s" % settings.SSL_DIR
        subprocess.call(shlex.split(cmd),
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
        
        
        # run the CH
        kill_old_procs(8000, 8001)
#        print "Running CH"
        cmd = "python %s -r %s -c %s -k %s -p 8001" % (
            join(settings.GCF_DIR, "gch.py"), join(settings.SSL_DIR, "ca.crt"),
            join(settings.SSL_DIR, "ch.crt"), join(settings.SSL_DIR, "ch.key")
        )
        args = shlex.split(cmd)
        self.ch_proc = subprocess.Popen(args,
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
        
        # run the AM proxy
#        print "Running AM Proxy"
        cmd = "python %s -r %s -c %s -k %s -p 8000" % (
            join(settings.GCF_DIR, "gam.py"), join(settings.SSL_DIR, "ca.crt"),
            join(settings.SSL_DIR, "server.crt"),
            join(settings.SSL_DIR, "server.key")
        )
        args = shlex.split(cmd)
        self.am_proc = subprocess.Popen(args,
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
        
        time.sleep(1)
        
        cert_transport = SafeTransportWithCert(
            keyfile=join(settings.SSL_DIR, "experimenter.key"),
            certfile=join(settings.SSL_DIR, "experimenter.crt"))
        self.ch_client = xmlrpclib.ServerProxy(
            "https://localhost:8001/",
            transport=cert_transport)
        
        cert_transport = SafeTransportWithCert(
            keyfile=join(settings.SSL_DIR, "experimenter.key"),
            certfile=join(settings.SSL_DIR, "experimenter.crt"))
        self.am_client = xmlrpclib.ServerProxy(
            "https://localhost:8000/",
            transport=cert_transport)

#        print "Done Setup"
        
    def tearDown(self):
        try:
            del self.switches
        except:
            pass
        try:
            del self.links
        except:
            pass
        
        try:
            self.am_proc.terminate()
        except:
            pass
        try:
            self.am_proc.terminate()
        except:
            pass

        import time
        time.sleep(1)
    
    def test_GetVersion(self):
        """
        Tests that get version returns 1.
        """
        self.assertEqual(self.am_client.GetVersion(), {'geni_api': 1})

    def test_ListResources(self):
        """
        Check the list of resources.
        """
        slice_urn, cred = self.create_ch_slice()
        options = dict(geni_compressed=False, geni_available=True)
        rspec = self.am_client.ListResources(cred, options)
        
#        print rspec
        
        # Create switches and links
        self.switches, self.links = parse_rspec(rspec)
        
        # check the number of switches and links
        self.assertEqual(len(self.switches),
                         settings.NUM_SWITCHES_PER_AGG * settings.NUM_DUMMY_OMS)
        self.assertEqual(len(self.links),
                         settings.NUM_LINKS_PER_AGG * settings.NUM_DUMMY_OMS)
    
    def test_CreateSliver(self):
        """
        Tests that we can create a sliver.
        """
        from clearinghouse.openflow.models import GAPISlice
        from clearinghouse.dummyom.models import DummyOMSlice
        
        # get the resources
        slice_urn, cred = self.create_ch_slice()
        options = dict(geni_compressed=False, geni_available=True)
        rspec = self.am_client.ListResources(cred, options)
        
        # Create switches and links
        self.switches, self.links = parse_rspec(rspec)

        # create a random reservation
        resv_rspec, flowspaces = create_random_resv(20, self.switches)
        self.am_client.CreateSliver(slice_urn, cred, resv_rspec)
        
        # TODO: check that the full reservation rspec is returned
        
        # check that all the switches are stored in the slice on the CH
        slice = GAPISlice.objects.get(slice_urn=slice_urn)
        dpids = []
        for fs in flowspaces:
            for switch in fs.switches:
                dpids.append(switch.dpid)
        dpids = set(dpids)
        # TODO: Do a better check
        self.assertEqual(len(dpids), len(slice.switches.all()))
        
        # check that the create_slice call has reached the dummyoms correctly
        # TODO: Do a better check
        self.assertEqual(len(DummyOMSlice.objects.all()),
                         settings.NUM_DUMMY_OMS)
        
    def test_CreateDeleteSliver(self):
        """
        Tests that we can create a sliver.
        """
        from clearinghouse.openflow.models import GAPISlice
        from clearinghouse.dummyom.models import DummyOMSlice
        
        # get the resources
        slice_urn, cred = self.create_ch_slice()
        options = dict(geni_compressed=False, geni_available=True)
        rspec = self.am_client.ListResources(cred, options)
        
        # Create switches and links
        self.switches, self.links = parse_rspec(rspec)

        # create a random reservation
        resv_rspec, flowspaces = create_random_resv(20, self.switches)
        self.am_client.CreateSliver(slice_urn, cred, resv_rspec)
        
        # delete the sliver
        self.assertTrue(self.am_client.DeleteSliver(slice_urn, cred))
        
        # Make sure it is gone from the CH and the OMs
        self.assertTrue(GAPISlice.objects.all().count() == 0,
                        "Slice not deleted in the Clearinghouse")
        self.assertTrue(DummyOMSlice.objects.all().count() == 0,
                        "Slice not deleted in the OMs")
         

    def test_parse_slice(self):
        from clearinghouse.openflow.models import GAPISlice
        from clearinghouse.dummyom.models import DummyOMSlice
        
        # get the resources
        slice_urn, cred = self.create_ch_slice()
        options = dict(geni_compressed=False, geni_available=True)
        rspec = self.am_client.ListResources(cred, options)
        
        # Create switches and links
        self.switches, self.links = parse_rspec(rspec)
        
        # create a random reservation
        vals = dict(
           firstname="John", lastname="Doe",
           email="john.doe@geni.net", password="slice_pass",
           proj_name="Stanford Networking",
           proj_desc="Making the world better.",
           slice_name="Crazy Load Balancer",
           slice_desc="Does this and that...",
           ctrl_url="tcp:controller.stanford.edu:6633")
        resv_rspec, flowspaces = create_random_resv(20, self.switches, **vals)
        
        from clearinghouse.openflow.gapi.rspec import parse_slice
        project_name, project_desc, slice_name, slice_desc,\
        controller_url, email, password, agg_slivers = parse_slice(resv_rspec)
        
        self.assertEqual(project_name, vals["proj_name"])
        self.assertEqual(project_desc, vals["proj_desc"])
        self.assertEqual(slice_name, vals["slice_name"])
        self.assertEqual(slice_desc, vals["slice_desc"])
        self.assertEqual(controller_url, vals["ctrl_url"])
        self.assertEqual(email, vals["email"])
        self.assertEqual(password, vals["password"])
        
        dpid_fs_map = {} # map dpid to requested fs
        for fs in flowspaces:
            for sw in fs.switches:
                if sw.dpid not in dpid_fs_map:
                    dpid_fs_map[int(sw.dpid)] = []
                dpid_fs_map[int(sw.dpid)].append(fs)
        
        # check that all slivers parsed are correct
        found_dpids = []
        for agg, slivers in agg_slivers:
            for sliver in slivers:
                found_dpids.append(int(sliver['datapath_id']))
                
                fs_set_requested = dpid_fs_map[int(sliver['datapath_id'])]
                fs_set_found = sliver['flowspace']
                
                # make sure that all the parsed flowspace was requested
                found = False
                for fs_found in fs_set_found:
                    for fs_req in fs_set_requested:
                        if fs_req.compare_to_sliver_fs(fs_found):
                            found = True
                            break
                self.assertTrue(found, 
                    "Didn't request flowspace %s for dpid %s" %\
                    (fs_found, sliver['datapath_id']))
                    
                # make sure that all requested flowspace was parsed
                found = False
                for fs_req in fs_set_requested:
                    for fs_found in fs_set_found:
                        if fs_req.compare_to_sliver_fs(fs_found):
                            found = True
                            break
                self.assertTrue(found,
                    "Didn't find requested flowspace %s for dpid %s" %\
                    (fs_found, sliver['datapath_id']))
                    
        # Check that each dpid is used only once
        self.assertTrue(len(found_dpids) == len(set(found_dpids)),
                        "Some dpids are used more than once.")
            
        
        # check that all requested slivers have been indeed parsed
        found_dpids = set(found_dpids)
        requested_dpids = set(dpid_fs_map.keys())
        self.assertEqual(found_dpids, requested_dpids)
            
        
if __name__ == '__main__':
    import unittest
    unittest.main()
  
