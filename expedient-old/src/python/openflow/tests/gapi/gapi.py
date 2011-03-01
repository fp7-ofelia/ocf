'''
Created on May 11, 2010

@author: jnaous
'''

import sys
from pprint import pformat
from os.path import join, dirname
import time
import subprocess
import shlex
PYTHON_DIR = join(dirname(__file__), "../../../")
sys.path.append(PYTHON_DIR)

from unittest import TestCase
import xmlrpclib
from openflow.tests import test_settings as settings
from openflow.tests.helpers import parse_rspec, create_random_resv, \
    kill_old_procs
from expedient.common.utils.certtransport import SafeTransportWithCert
from expedient.common.tests.commands import call_env_command, Env

ch_env = Env(settings.CH_PROJECT_DIR)
ch_env.switch_to()

if settings.SHOW_PROCESSES_IN_XTERM:
    from expedient.common.tests.utils import run_cmd_in_xterm as run_cmd
else:
    from expedient.common.tests.utils import run_cmd
from expedient.common.tests.utils import wrap_xmlrpc_call, drop_to_shell
from expedient.common.tests.client import Browser

import logging
logger = logging.getLogger("openflow.tests.gapi")

SCHEME = "https" if settings.USE_HTTPS else "http"

def get_base_url(path):
    return SCHEME + "://%s:%s%s%s" % (
        settings.HOST, settings.CH_PORT, settings.PREFIX, path)

class GAPITests(TestCase):
    """
    Test the GENI API interface. This assumes that Apache is currently running
    Expedient over SSL. Expedient will be contacting itself as
    the dummy Opt-in Managers. Assumes all certificates and keys in ssl dir.
    """

    def create_ch_slice(self):
        """
        Code mostly copied from GENI test harness from BBN.
        """
        import gcf.sfa.trust.credential as cred
        
        slice_cred_string = wrap_xmlrpc_call(
            self.ch_client.CreateSlice, [], {}, settings.TIMEOUT)
        slice_credential = cred.Credential(string=slice_cred_string)
        slice_gid = slice_credential.get_gid_object()
        slice_urn = slice_gid.get_urn()
        
        # Set up the array of credentials as just the slice credential
        credentials = [slice_cred_string]
        
        return (slice_urn, credentials)
        
    def setup_dummy_oms(self):
        from openflow.dummyom.models import DummyOM
        from django.contrib.auth.models import User
        from django.core.urlresolvers import reverse
        
        for i in range(settings.NUM_DUMMY_OMS):
            # Create the OM user
            username = "clearinghouse%s" % i
            password = "clearinghouse"
            User.objects.create_user(
                username=username, email="email@email.com", password=password)

            # Create the Dummy OM to which we will connect
            om = DummyOM.objects.create()
            om.populate_links(settings.NUM_SWITCHES_PER_AGG, 
                              settings.NUM_LINKS_PER_AGG/2)
            
            logger.debug("Creating OpenFlow Aggregate %s" % (i+1))
            
            # Add the dummy OM aggregate to Expedient
            response = self.browser.get_and_post_form(
                url=get_base_url(reverse("openflow_aggregate_create")),
                params=dict(
                    name="DummyOM %s" % i,
                    description="DummyOM Description",
                    location="Stanford, CA",
                    usage_agreement="Do you agree?",
                    username=username,
                    password=password,
                    url=get_base_url(reverse("dummyom_rpc", args=[om.id])),
                ),
                del_params=["verify_certs"],
            )
            self.assertEqual(
                response.geturl(),
                get_base_url(
                    reverse("openflow_aggregate_add_links", args=[i+1])),
                "Did not redirect after create correctly. Response was: %s"
                % response.read(),
            )
        
    def create_users(self):
        from django.contrib.auth.models import User
        
        User.objects.create_superuser(
            "expedient", "email@email.com", "expedient")
        
    def setUp(self):
        """
        Load the DB fixtures for the AM (running using Apache).
        Create an xml-rpc client to talk to the AM Proxy through GAPI.
        Run the test Expedient, and create client to talk to it.
        """
        
        import time, httplib, os
        
        call_env_command(settings.CH_PROJECT_DIR, "flush", interactive=False)
        call_env_command(settings.CH_PROJECT_DIR, "syncdb", interactive=False)

        logger.debug("setup started")
        
        # now we can import django stuff
        from django.core.urlresolvers import reverse
        from django.conf import settings as djangosettings
        from openflow.plugin.models import OpenFlowAggregate

        self.assertEqual(OpenFlowAggregate.objects.all().count(), 0)

        self.create_users()
        
        self.browser = Browser()
        self.browser.login(get_base_url(reverse("auth_login")),
                           username="expedient",
                           password="expedient")
        
        self.setup_dummy_oms()
        
        # store the trusted CA dir
        self.before = os.listdir(djangosettings.XMLRPC_TRUSTED_CA_PATH)
        
        # Create the ssl certificates
        cmd = "make -C %s" % settings.SSL_DIR
        run_cmd(cmd).wait()
        
        # add the certificate to apache's certificate dir
        try:
            os.unlink(join(settings.APACHE_CERTS_DIR, "test-ca.crt"))
        except OSError as e:
            if "Errno 2" in "%s" % e:
                pass
            else:
                raise
        os.symlink(
            os.path.abspath(join(settings.SSL_DIR, "ca.crt")),
            join(settings.APACHE_CERTS_DIR, "test-ca.crt")
        )
        subprocess.call(shlex.split("make -C %s" % settings.APACHE_CERTS_DIR))
        
        # run the CH
        kill_old_procs(settings.GCH_PORT, settings.GAM_PORT)
        cmd = "python %s -u %s -r %s -c %s -k %s -p %s --debug -H 0.0.0.0" % (
            join(settings.GCF_DIR, "gch.py"),
            join(settings.SSL_DIR, "experimenter.crt"),
            join(settings.SSL_DIR, "certs"),
            join(settings.SSL_DIR, "ch.crt"), join(settings.SSL_DIR, "ch.key"),
            settings.GCH_PORT,
        )
        self.ch_proc = run_cmd(cmd, pause=True)
        
#        # run the AM proxy
#        cmd = "python %s -r %s -c %s -k %s -p %s -u %s --debug -H 0.0.0.0" % (
#            join(settings.GCF_DIR, "gam.py"),
#            join(settings.SSL_DIR, "certs"),
#            join(settings.SSL_DIR, "server.crt"),
#            join(settings.SSL_DIR, "server.key"),
#            settings.GAM_PORT,
#            SCHEME + "://%s:%s/openflow/gapi/" % (settings.HOST, settings.CH_PORT),
#        )
#        self.am_proc = run_cmd(cmd, pause=True)
        
        ch_host = "%s:%s" % (settings.HOST, settings.GCH_PORT)
        cert_transport = SafeTransportWithCert(
            keyfile=join(settings.SSL_DIR, "experimenter.key"),
            certfile=join(settings.SSL_DIR, "experimenter.crt"))
        self.ch_client = xmlrpclib.ServerProxy(
            "https://"+ch_host+"/",
            transport=cert_transport)
        
        am_host = "%s:%s" % (settings.HOST, settings.CH_PORT)
        cert_transport = SafeTransportWithCert(
            keyfile=join(settings.SSL_DIR, "experimenter.key"),
            certfile=join(settings.SSL_DIR, "experimenter.crt"))
        self.am_client = xmlrpclib.ServerProxy(
            "https://"+am_host+"/openflow/gapi/",
            transport=cert_transport)
        
        logger.debug("setup done")
        
    def tearDown(self):
        # restore the trusted CA dir
        from django.conf import settings as djangosettings
        import os
        after = os.listdir(djangosettings.XMLRPC_TRUSTED_CA_PATH)
        for path in after:
            if path not in self.before:
                os.unlink(os.path.join(djangosettings.XMLRPC_TRUSTED_CA_PATH, path))

        if settings.PAUSE_AFTER_TESTS:
            raw_input("Press ENTER to continue:")
        
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
            self.ch_proc.terminate()
        except:
            pass

        import time
        time.sleep(4)
    
    def test_GetVersion(self):
        """
        Tests that get version returns 1.
        """
        ret = wrap_xmlrpc_call(
            self.am_client.GetVersion, [], {}, settings.TIMEOUT)
        self.assertEqual(ret['geni_api'], 1)

    def test_ListResources(self, zipped=False):
        """
        Check the list of resources.
        """
        from openflow.dummyom.models import DummyOM
        slice_urn, cred = self.create_ch_slice()
        options = dict(geni_compressed=zipped, geni_available=True)
        rspec = wrap_xmlrpc_call(
            self.am_client.ListResources,
            [cred, options], {}, settings.TIMEOUT)
        
        logger.debug("Got Advertisement RSpec: \n%s" % rspec)
        
        if zipped:
            import zlib, base64
            rspec = zlib.decompress(base64.b64decode(rspec))
        
        # Create switches and links
        self.switches, self.links = parse_rspec(rspec)
        
        # check the number of switches and links
        num_links = sum([len(d.get_switches()) for d in DummyOM.objects.all()])
        self.assertEqual(len(self.switches),
                         num_links)
        self.assertEqual(len(self.links),
                         settings.NUM_LINKS_PER_AGG * settings.NUM_DUMMY_OMS)

    def test_ZippedListResources(self):
        """
        Check the list of resources.
        """
        self.test_ListResources(zipped=True)

    def test_topoChange_ListResources(self):
        """
        Check the list of resources before and after a topology change
        """
        from openflow.dummyom.models import DummyOM
        
        slice_urn, cred = self.create_ch_slice()
        options = dict(geni_compressed=False, geni_available=True)
        rspec = wrap_xmlrpc_call(
            self.am_client.ListResources,
            [cred, options], {}, settings.TIMEOUT)
        
        # Create switches and links
        self.switches, self.links = parse_rspec(rspec)
        
        # check the number of switches and links
        num_links = sum([len(d.get_switches()) for d in DummyOM.objects.all()])
        self.assertEqual(len(self.switches),
                         num_links)
        self.assertEqual(len(self.links),
                         settings.NUM_LINKS_PER_AGG*settings.NUM_DUMMY_OMS)
        
        killed_dpids = []
        for om in DummyOM.objects.all():
            killed_dpids.append(om.kill_dpid())
            om.dummycallbackproxy.call_back()
            
        # Create switches and links
        options = dict(geni_compressed=False, geni_available=True)
        rspec = self.am_client.ListResources(cred, options)
        self.switches, self.links = parse_rspec(rspec)
        
        # check the number of switches
        num_links = sum([len(d.get_switches()) for d in DummyOM.objects.all()])
        self.assertEqual(len(self.switches),
                         num_links)
        
        # make sure all killed dpids are gone: None of the dpids still
        # here should have the dpid of a killed switch.
        for s in self.switches:
            for d in killed_dpids:
                self.assertNotEqual(str(s.dpid), str(d))
        
    def test_CreateSliver(self):
        """
        Tests that we can create a sliver.
        """
        from openflow.plugin.models import OpenFlowSwitch
        from openflow.dummyom.models import DummyOMSlice
        from expedient.clearinghouse.slice.models import Slice
        
        # get the resources
        slice_urn, cred = self.create_ch_slice()
        options = dict(geni_compressed=False, geni_available=True)
        rspec = wrap_xmlrpc_call(
            self.am_client.ListResources,
            [cred, options], {}, settings.TIMEOUT)
        
        # Create switches and links
        self.switches, self.links = parse_rspec(rspec)

        # create a random reservation
        resv_rspec, flowspaces = create_random_resv(20, self.switches)
        users = [{'key':''}]
        ret = self.am_client.CreateSliver(slice_urn, cred, resv_rspec, users)
        
        self.assertEqual(resv_rspec, ret)
        
        # check that all the switches are stored in the slice on the CH
        slice = Slice.objects.get(gapislice__slice_urn=slice_urn)
        
        switches = OpenFlowSwitch.objects.filter(
            openflowinterface__slice_set=slice).distinct()
        
        dpids = []
        for fs in flowspaces:
            for switch in fs.switches:
                dpids.append(switch.dpid)
        dpids = set(dpids)
        
        # TODO: Do a better check
        self.assertEqual(len(dpids), len(switches))
        
        # check that the create_slice call has reached the dummyoms correctly
        # TODO: Do a better check
        self.assertEqual(len(DummyOMSlice.objects.all()),
                         settings.NUM_DUMMY_OMS)

        # TODO: check the listresources call for the slice
        
        
    def test_CreateDeleteSliver(self):
        """
        Tests that we can create a sliver.
        """
        from expedient.clearinghouse.slice.models import Slice
        from openflow.dummyom.models import DummyOMSlice
        
        # get the resources
        slice_urn, cred = self.create_ch_slice()
        options = dict(geni_compressed=False, geni_available=True)
        rspec = wrap_xmlrpc_call(
            self.am_client.ListResources,
            [cred, options], {}, settings.TIMEOUT)
        
        # Create switches and links
        self.switches, self.links = parse_rspec(rspec)

        # create a random reservation
        resv_rspec, flowspaces = create_random_resv(20, self.switches)
        users = [{'key':''}]
        self.am_client.CreateSliver(slice_urn, cred, resv_rspec, users)
        
        # delete the sliver
        self.assertTrue(self.am_client.DeleteSliver(slice_urn, cred))
        
        time.sleep(5)
        
        # Make sure it is gone from the CH and the OMs
        self.assertTrue(Slice.objects.all().count() == 0,
                        "Slice not deleted in Expedient")
        self.assertTrue(DummyOMSlice.objects.all().count() == 0,
                        "Slice not deleted in the OMs")
         
    def test_parse_slice(self):
        from openflow.plugin.gapi.rspec import parse_slice
        
        # get the resources
        slice_urn, cred = self.create_ch_slice()
        options = dict(geni_compressed=False, geni_available=True)
        rspec = wrap_xmlrpc_call(
            self.am_client.ListResources,
            [cred, options], {}, settings.TIMEOUT)
        
        logger.debug("Got RSpec\n%s" % rspec)
        
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
        resv_rspec, flowspaces = create_random_resv(2, self.switches, **vals)
        
        project_name, project_desc, slice_name, slice_desc,\
        controller_url, email, password, iface_fs_map = parse_slice(resv_rspec)
        
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
                    dpid_fs_map[sw.dpid] = []
                dpid_fs_map[sw.dpid].append(fs)
        
        logger.debug(iface_fs_map)
#        # check that all slivers parsed are correct
#        for iface, fs_set in iface_fs_map.items():
#            
#        found_dpids = []
#        for sliver in slivers:
#            for sliver in slivers:
#                found_dpids.append(sliver['datapath_id'])
#                
#                fs_set_requested = dpid_fs_map[sliver['datapath_id']]
#                fs_set_found = sliver['flowspace']
#                
#                # make sure that all the parsed flowspace was requested
#                for fs_found in fs_set_found:
#                    found = False
#                    for fs_req in fs_set_requested:
#                        if fs_req.compare_to_sliver_fs(fs_found):
#                            found = True
#                            break
#                    self.assertTrue(found,
#                        "Didn't request flowspace %s for dpid %s\n" %\
#                        (pformat(fs_found), sliver['datapath_id']) +
#                        "Flowspaces parsed:\n%s\nFlowspaces requested:\n%s"
#                        % (pformat(fs_set_found),
#                           pformat( [f.get_full_attrs()
#                                     for f in fs_set_requested]))
#                    )
#                    
#                # make sure that all requested flowspace was parsed
#                for fs_req in fs_set_requested:
#                    found = False
#                    for fs_found in fs_set_found:
#                        if fs_req.compare_to_sliver_fs(fs_found):
#                            found = True
#                            break
#                    self.assertTrue(found,
#                        "Didn't find requested flowspace %s for dpid %s" %\
#                        (fs_found, sliver['datapath_id']))
                    
#        # Check that each dpid is used only once
#        self.assertTrue(len(found_dpids) == len(set(found_dpids)),
#                        "Some dpids are used more than once.")
#            
#        # check that all requested slivers have been indeed parsed
#        found_dpids = set(found_dpids)
#        requested_dpids = set(dpid_fs_map.keys())
#        self.assertEqual(found_dpids, requested_dpids)
            
        
if __name__ == '__main__':
    import unittest
    unittest.main()
  
