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
        print "Creating Dummy OMs and adding them"
        
        from commands import call_env_command
        import shlex, subprocess, time
        
        call_env_command(settings.CH_PROJECT_DIR, "flush", interactive=False)
        call_env_command(settings.CH_PROJECT_DIR, "runscript", "populate_am")
        
        print "Creating certs"
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
  