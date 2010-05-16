'''
Created on May 11, 2010

@author: jnaous
'''

from django.test import TestCase 
from transport import SafeTransportWithCert
from pprint import pprint
import xmlrpclib
from clearinghouse.dummyom.models import DummyOM
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from clearinghouse.xmlrpc_serverproxy.models import PasswordXMLRPCServerProxy
import socket
from clearinghouse.openflow.models import OpenFlowAggregate
from os.path import join, dirname

class GAPITests(TestCase):
    """
    Test the GENI API interface. This assumes that Apache is currently running
    the clearinghouse over SSL. The clearinghouse will be contacting itself as
    the dummy Opt-in Managers. Assumes all certificates and keys in ssl dir.
    """
    
    NUM_SWITCHES_PER_AGG = 10
    NUM_LINKS_PER_AGG = 20
    NUM_OMS = 3
    SSL_DIR = join(dirname(__file__), "ssl")
    HOST = socket.getfqdn()
    PORT = 443
    PREFIX = ""
    GCF_DIR = join(dirname(__file__), "../../../gcf")
    
    def create_ch_slice(self):
        """
        Code mostly copied from GENI test harness from BBN.
        """
        import sfa.trust.credential as cred
        
        slice_cred_string = self.ch_client.CreateSlice()
        slice_credential = cred.Credential(string=slice_cred_string)
        slice_gid = slice_credential.get_gid_object()
        slice_urn = slice_gid.get_urn()
        print 'Slice URN = %s' % (slice_urn)
        
        # Set up the array of credentials as just the slice credential
        credentials = [slice_cred_string]
        
        return (slice_urn, credentials)
        
    def _kill_old_ch_proc(self):
        import shlex, subprocess, os, signal, time
        cmd = "netstat -l -t -p --numeric-ports"
        args = shlex.split(cmd)
        p = subprocess.Popen(args,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        p.wait()
        o, e = p.communicate()
        lines = o.splitlines()
        for l in lines:
            if "localhost:8001" in l:
                cols = l.split()
                prog = cols[6]
                pid,sep,progname = prog.partition("/")
                os.kill(int(pid), signal.SIGHUP)
                time.sleep(1)
                return
        
        
    def setUp(self):
        """
        Create dummy OMs and add to AM
        Create users for the AM.
        Create an xml-rpc client to talk to the AM through GAPI.
        Run the test clearinghouse, and create client to talk to it.
        """
        print "Creating Dummy OMs and adding them"
        # Dummy OMs
        for i in range(3):
            om = DummyOM.objects.create()
            om.populate_links(self.NUM_SWITCHES_PER_AGG, self.NUM_LINKS_PER_AGG)
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
                    self.HOST, self.PORT, self.PREFIX, om.id,
                ),
                verify_certs = False,
            )
            # test availability
            print "Checking availability."
            if not proxy.is_available:
                raise Exception("Problem: Proxy not available")
            # Add aggregate
            of_agg = OpenFlowAggregate.objects.create(
                name=username,
                description="hello",
                location="America",
                client=proxy,
            )
            err = of_agg.setup_new_aggregate(self.HOST)
            if err:
                raise Exception("Error setting up aggregate: %s" % err)
        
        # create the xml-rpc client
        print "Creating xml-rpc clients"
        cert_transport = SafeTransportWithCert(
            keyfile=join(self.SSL_DIR, "experimenter.key"),
            certfile=join(self.SSL_DIR, "experimenter.crt"))
        self.client = xmlrpclib.ServerProxy(
            "https://%s:%s/%sopenflow/gapi/" % (
                self.HOST, self.PORT, self.PREFIX,
            ),
            transport=cert_transport)
        
        # run the CH
        self._kill_old_ch_proc()
        import shlex, subprocess, time
        print "Running CH"
        cmd = "python %s -r %s -c %s -k %s -p 8001" % (
            join(self.GCF_DIR, "gch.py"), join(self.SSL_DIR, "ca.crt"),
            join(self.SSL_DIR, "ch.crt"), join(self.SSL_DIR, "ch.key")
        )
        args = shlex.split(cmd)
        self.ch_proc = subprocess.Popen(args,
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
        time.sleep(1)
        
        cert_transport = SafeTransportWithCert(
            keyfile=join(self.SSL_DIR, "experimenter.key"),
            certfile=join(self.SSL_DIR, "experimenter.crt"))
        self.ch_client = xmlrpclib.ServerProxy(
            "https://localhost:8001/",
            transport=cert_transport)
        
        
    def tearDown(self):
        try:
            self.ch_proc.self.ch_proc.terminate()
        except:
            pass
        import time
        time.sleep(1)
    
    def test_0GetVersion(self):
        """
        Tests that get version returns 1.
        """
        self.assertEqual(self.client.GetVersion(), {'geni_api': 1})
        
    def test_1ListResources(self):
        """
        Check the list of resources.
        """
        slice_urn, cred = self.create_ch_slice()
        options = dict(geni_compressed=False, geni_available=True)
        print self.client.ListResources(cred, options)
    
    def test_2CreateSliver(self):
        """
        Tests that we can create a sliver.
        """
        pass
        
        
        