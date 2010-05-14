'''
Created on May 11, 2010

@author: jnaous
'''
from unittest import TestCase
from transport import SafeTransportWithCert
import xmlrpclib
import socket
from os.path import join, dirname
from tests import settings
import re
from clearinghouse.openflow.gapi.rspec import RESV_RSPEC_TAG, FLOWSPACE_TAG,\
    SWITCHES_TAG, SWITCH_TAG, URN

SWITCH_URN_REGEX = "^(?P<prefix>.*)\+switch:(?P<dpid>\d+)$"
PORT_URN_REGEX = "%s\+port:(?P<port>\d+)$" % SWITCH_URN_REGEX

class CH_OM_Tests(TestCase):
    """
    Test the integration between the CH (aka AM) and the OM.
    """

    def setUp(self):
        """
        Load the CH and OM fixtures.
        """
        pass

    def test_create_slice(self):
        """
        Tests the create slice rpc call.
        """
        pass

class GAPITests(TestCase):
    """
    Test the GENI API interface. This assumes that Apache is currently running
    the clearinghouse over SSL. The clearinghouse will be contacting itself as
    the dummy Opt-in Managers. Assumes all certificates and keys in ssl dir.
    """

    class Switch(object):
        def __init__(self, urn):
            match = re.search(SWITCH_URN_REGEX, urn)
            if not match:
                raise Exception("Bad switch URN: %s" % urn)
            self.prefix = match.group("prefix")
            self.dpid = match.group("dpid")
            self.urn = urn
            
        def add_to_switches_resv_elem(self, switches_elem):
            from xml.etree import cElementTree as et
            return et.SubElement(
                switches_elem, SWITCH_TAG, {
                    URN: self.urn,
                }
            )
            
    class Link(object):
        def __init__(self, src_urn, dst_urn):
            self.src_urn = src_urn
            self.dst_urn = dst_urn

            match = re.search(PORT_URN_REGEX, src_urn)
            if not match:
                raise Exception("Bad port URN: %s" % src_urn)
            self.src_prefix = match.group("prefix")
            self.src_dpid = match.group("dpid")
            self.src_port = match.group("port")
            
            match = re.search(PORT_URN_REGEX, dst_urn)
            if not match:
                raise Exception("Bad port URN: %s" % dst_urn)
            self.dst_prefix = match.group("prefix")
            self.dst_dpid = match.group("dpid")
            self.dst_port = match.group("port")
            
    class Flowspace(object):
        def __init__(self, attrs, switches):
            """
            attrs is a dict with the following keys:
            dl_src/dst/type
            vlan_id
            nw_src/dst/type
            tp_src/dst
            
            Each key maps to a tuple specifying a range. e.g.
            {'dl_src': ('*', '*'),
             'nw_src': ('192.168.0.0', '192.168.255.255'),
            }
            
            Some keys can be missing.
             
            switches is a list of Switch objects
            """
            self.attrs = attrs.copy()
            self.switches = switches
            
        def add_to_rspec(self, root):
            from xml.etree import cElementTree as et
            fs_elem = et.SubElement(root, FLOWSPACE_TAG)
            switches_elem = et.SubElement(fs_elem, SWITCHES_TAG)
            for s in self.switches:
                s.add_to_switches_resv_elem(switches_elem)

            fset.SubElement(
                switches_elem, 

            for k, v in self.attrs.items():
    def parse_rspec(self, rspec):
        """
        parse the rspec and return a tupe of lists of switches and links
        """
        from xml.etree import cElementTree as et
        
        root = et.fromstring(rspec)
        # TODO: finish this parsing up.
    
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
        
    def _kill_old_procs(self):
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
            if "localhost:8000" in l:
                cols = l.split()
                prog = cols[6]
                pid,sep,progname = prog.partition("/")
                os.kill(int(pid), signal.SIGHUP)
        
        time.sleep(1)
            
    def setUp(self):
        """
        Load the DB fixtures for the AM (running using Apache).
        Create an xml-rpc client to talk to the AM Proxy through GAPI.
        Run the test clearinghouse, and create client to talk to it.
        """
        print "Doing Setup"
        
        from commands import call_env_command
        import shlex, subprocess, time
        
        call_env_command(settings.CH_PROJECT_DIR, "flush", interactive=False)
        call_env_command(settings.CH_PROJECT_DIR, "runscript", "populate_am", noscripts=False)
        
        cmd = "make -C %s" % settings.SSL_DIR
        self.ch_proc = subprocess.call(shlex.split(cmd),
                                       stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
        
        
#        # run the CH
#        self._kill_old_procs()
#        print "Running CH"
#        cmd = "python %s -r %s -c %s -k %s -p 8001" % (
#            join(settings.GCF_DIR, "gch.py"), join(settings.SSL_DIR, "ca.crt"),
#            join(settings.SSL_DIR, "ch.crt"), join(settings.SSL_DIR, "ch.key")
#        )
#        args = shlex.split(cmd)
#        self.ch_proc = subprocess.Popen(args,
#                                        stdin=subprocess.PIPE,
#                                        stdout=subprocess.PIPE,
#                                        stderr=subprocess.PIPE)
#
#        # run the AM proxy
#        print "Running AM Proxy"
#        cmd = "python %s -r %s -c %s -k %s -p 8000" % (
#            join(settings.GCF_DIR, "gam.py"), join(settings.SSL_DIR, "ca.crt"),
#            join(settings.SSL_DIR, "server.crt"),
#            join(settings.SSL_DIR, "server.key")
#        )
#        args = shlex.split(cmd)
#        self.am_proc = subprocess.Popen(args,
#                                        stdin=subprocess.PIPE,
#                                        stdout=subprocess.PIPE,
#                                        stderr=subprocess.PIPE)
#        
#        time.sleep(1)
        
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

        print "Done Setup"
        
#    def tearDown(self):
#        try:
#            self.ch_proc.terminate()
#            self.am_proc.terminate()
#        except:
#            pass
#        import time
#        time.sleep(1)
    
    def test_0GetVersion(self):
        """
        Tests that get version returns 1.
        """
        self.assertEqual(self.am_client.GetVersion(), {'geni_api': 1})

    def test_1ListResources(self):
        """
        Check the list of resources.
        """
        slice_urn, cred = self.create_ch_slice()
        options = dict(geni_compressed=False, geni_available=True)
        print self.am_client.ListResources(cred, options)
    
    def test_2CreateSliver(self):
        """
        Tests that we can create a sliver.
        """
        pass
        
        
if __name__ == '__main__':
    import unittest
    unittest.main()
  
