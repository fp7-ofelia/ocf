'''
Created on Jun 30, 2010

@author: jnaous
'''
import sys
from os.path import join, dirname
PYTHON_DIR = join(dirname(__file__), "../../../")
sys.path.append(PYTHON_DIR)

from unittest import TestCase
from expedient.common.utils.certtransport import SafeTransportWithCert
from openflow.tests import test_settings
import xmlrpclib, re
from openflow.tests.helpers import kill_old_procs, parse_rspec, Flowspace
from openflow.tests.helpers import create_random_resv
import time

import logging
logger = logging.getLogger("PostDeploymentTest")

SCHEME = "https" if test_settings.USE_HTTPS else "http"

class Tests(TestCase):

    def create_ch_slice(self):
        """
        Code mostly copied from GENI test harness from BBN.
        """
        import gcf.sfa.trust.credential as cred
        
        slice_cred_string = self.ch_client.CreateSlice()
        slice_credential = cred.Credential(string=slice_cred_string)
        slice_gid = slice_credential.get_gid_object()
        slice_urn = slice_gid.get_urn()
        
        # Set up the array of credentials as just the slice credential
        credentials = [slice_cred_string]
        
        return (slice_urn, credentials)

    def setUp(self):
        """
        Create clients at the Flowviso
        """
        cert_transport = SafeTransportWithCert(
            keyfile=join(test_settings.SSL_DIR, "experimenter.key"),
            certfile=join(test_settings.SSL_DIR, "experimenter.crt"))
        self.am_client = xmlrpclib.ServerProxy(
            "https://localhost:8000/",
            transport=cert_transport)
        
        cert_transport = SafeTransportWithCert(
            keyfile=join(test_settings.SSL_DIR, "experimenter.key"),
            certfile=join(test_settings.SSL_DIR, "experimenter.crt"))
        self.ch_client = xmlrpclib.ServerProxy(
            "https://localhost:8001/",
            transport=cert_transport)
        
        flowvisor = test_settings.FLOWVISORS[0]
        fv_url = "https://%s:%s@%s:%s" % (
            flowvisor["username"], flowvisor["password"],
            flowvisor["host"], flowvisor["xmlrpc_port"],
        )
        self.fv_client = xmlrpclib.ServerProxy(fv_url)

    def test_GetVersion(self):
        """
        Get Version.
        """
        version = self.am_client.GetVersion()
        self.assertEqual(version['geni_api'], 1)

    def test_ListCreateDelete(self):
        """
        List resources, createsliver, opt-in, deletesliver.
        """
        ###### ListResources ######
        slice_urn, cred = self.create_ch_slice()
        options = dict(geni_compressed=False, geni_available=True)
        rspec = self.am_client.ListResources(cred, options)
        
        logger.debug(rspec)
        
        # Create switches and links
        self.switches, self.links = parse_rspec(rspec)
        
        # check the number of switches and links
        logger.debug("Found the following switches: %s" % self.switches)
        logger.debug("Found the following links: %s" % self.links)
        
        slices_before = self.fv_client.api.listSlices()
        logger.debug("Slices at the FlowVisor before creating slice: %s" %
            slices_before)

        ###### CreateSliver ######

        # create a random reservation
        slice_name = "SliceNameBla"
        email = "john.doe@geni.net"
        url = "tcp:%s:%s" % (test_settings.CONTROLLER_HOST,
                             test_settings.CONTROLLER_PORT)
        fs = [
            Flowspace({"tp_dst": (80, 80)}, self.switches()),
            Flowspace({"tp_src": (80, 80)}, self.switches()),
        ]
        
        resv_rspec, flowspaces = create_random_resv(
            2, self.switches,
            slice_name=slice_name,
            email=email,
            ctrl_url=url,
            flowspaces=[fs],
        )
        
        logger.debug("RSpec returned by reservation: %s" % 
            self.am_client.CreateSliver(slice_urn, cred, resv_rspec))
        
        slices_after = self.fv_client.api.listSlices()
        logger.debug("Slices at the FlowVisor after creation: %s" %
            slices_after)
        
        slices_new = set(slices_after) - set(slices_before)
        logger.debug("Created: %s" % slices_new)
        self.assertEqual(len(slices_new), 1)
        
        slice_name = slices_new.pop()
        
        logger.debug("Slice information at the FlowVisor %s" %
            self.fv_client.api.getSliceInfo(slice_name))
        
        ###### Opt-In ######
        flowspace = self.fv_client.api.listFlowSpace()
        logger.debug("FlowSpace before opt-in: %s" % flowspace)
        
        raw_input("Now opt-in a user to the slice and press Enter when done.")
        
        flowspace = self.fv_client.api.listFlowSpace()
        logger.debug("FlowSpace after opt-in: %s" % flowspace)
        
        ###### Opt-Out ######
        flowspace = self.fv_client.api.listFlowSpace()
        logger.debug("FlowSpace before opt-out: %s" % flowspace)
        
        raw_input("Now opt-out the user from the slice and press Enter when done.")
        
        flowspace = self.fv_client.api.listFlowSpace()
        logger.debug("FlowSpace after opt-out: %s" % flowspace)
        
        ###### DeleteSliver ######
        slices_before = self.fv_client.api.listSlices()
        logger.debug("Slices at the FlowVisor before deleting slice: %s" %
            slices_before)

        self.assertTrue(
            self.am_client.DeleteSliver(slice_urn, cred),
            "Failed to delete sliver.")
        
        slices_after = self.fv_client.api.listSlices()
        logger.debug("Slices at the FlowVisor after deleting slice: %s" %
            slices_before)
