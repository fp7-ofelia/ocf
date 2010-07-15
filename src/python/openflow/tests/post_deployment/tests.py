'''
Created on Jun 30, 2010

@author: jnaous
'''
import sys
from os.path import join, dirname
import random
PYTHON_DIR = join(dirname(__file__), "../../../")
sys.path.append(PYTHON_DIR)

from unittest import TestCase
from expedient.common.utils.certtransport import SafeTransportWithCert
import xmlrpclib
from openflow.tests.helpers import parse_rspec, Flowspace
from openflow.tests.helpers import create_random_resv
from expedient.common.tests.utils import drop_to_shell
import logging
from expedient.common import loggingconf
loggingconf.set_up(logging.DEBUG) # Change logging.INFO for less output

logger = logging.getLogger("PostDeploymentTest")

# Set this to "http" if you know the server uses HTTP instead of HTTPS.
SCHEME = "https"

# Settings for the flowvisor to verify slice creation and opt-in.
FLOWVISOR = dict(
    host="beirut.stanford.edu",   # host for flowvisor's interface
    xmlrpc_port=8080,         # XMLRPC port for the flowvisor
    username="root",          # The username to use to connect to the FV
    password="rootpassword",        # The password to use to connect to the FV
)

# The URL for the GAPI proxy you want to use to communicate with Expedient
GAM_URL = "https://beirut.stanford.edu:8000/"

# The URL to the GENI Clearinghouse that gives out the credentials.
GCH_URL = "https://beirut.stanford.edu:8001/"

# Where is the SSL certificate stored?
SSL_DIR = "/home/expedient/gapi-ssl"

# What is the first part of the filename of the experimenter's cert and key?
CERTKEY_FILENAME = "experimenter" # experimenter.key and experimenter.crt

# The location of the controller for the slice. If you are just testing the
# gapi interface and not interested in actually seeing traffic at a controller,
# you can set these to an arbitrary value.
CONTROLLER_URL = "tcp:localhost:6633"

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
        Create clients at the Flowvisor
        """
        cert_transport = SafeTransportWithCert(
            keyfile=join(SSL_DIR, "%s.key" % CERTKEY_FILENAME),
            certfile=join(SSL_DIR, "%s.crt" % CERTKEY_FILENAME))
        self.am_client = xmlrpclib.ServerProxy(
            GAM_URL,
            transport=cert_transport)
        
        cert_transport = SafeTransportWithCert(
            keyfile=join(SSL_DIR, "%s.key" % CERTKEY_FILENAME),
            certfile=join(SSL_DIR, "%s.crt" % CERTKEY_FILENAME))
        self.ch_client = xmlrpclib.ServerProxy(
            GCH_URL,
            transport=cert_transport)
        
        flowvisor = FLOWVISOR
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
        slice_name = "SliceNameBla %s" % random.randint(1, 10000000)
        email = "john.doe@geni.net"
        url = CONTROLLER_URL
        
        fs = [
            Flowspace({"tp_dst": ("80", "80")}, self.switches),
            Flowspace({"tp_src": ("80", "80")}, self.switches),
        ]
        
        logger.debug("Flowspace: [%s, %s]" % (fs[0], fs[1]))
        
        resv_rspec, flowspaces = create_random_resv(
            2, self.switches,
            slice_name=slice_name,
            email=email,
            ctrl_url=url,
            flowspaces=fs,
        )
        
        logger.debug("Reservation rspec: %s" % resv_rspec)
        logger.debug("Flowspaces in rspec: [%s, %s]" % 
                     (flowspaces[0], flowspaces[1]))
        
        raw_input("Press Enter to proceed with the reservation:")
        
        logger.debug("RSpec returned by reservation: %s" % 
            self.am_client.CreateSliver(slice_urn, cred, resv_rspec,
                                        users=[]))
        
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
            slices_after)

if __name__ == '__main__':
    import unittest
    unittest.main()
  
