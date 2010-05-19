'''
Created on May 17, 2010

@author: jnaous
'''
from unittest import TestCase
from tests.transport import SafeTransportWithCert
import test_settings

class FullIntegration(TestCase):
    MININET_TOPO = "linear,2"
    NOX_APPS = "pyswitch packetdump"
    
    def run_nox(self, mininet_vm, num, port_start):
        """
        Connect to the mininet_vm and run 'num' instances of nox as
        a pyswitch with packet dumping.
        """
        from paramiko import SSHClient, AutoAddPolicy
        
        self.nox_clients = []
        for i in xrange(num):
            port = port_start + i

            client = SSHClient()
            client.set_missing_host_key_policy(AutoAddPolicy())
            client.connect(
                mininet_vm, username="mininet", password="mininet",
            )
            stdin, stdout, stderr = client.exec_command(
                "cd noxcore/build/src; ./nox_core -i ptcp:%s %s" % (
                    port, self.NOX_APPS,
                )
            )
            
            self.nox_clients.append((stdin, stdout, stderr, client))
        
    def connect_networks(self, flowvisors, mininet_vms):
        """
        Create a 2-switch, 2-host linear topology on each mininet vm
        Connect the switches to the FV.
        """
        from paramiko import SSHClient, AutoAddPolicy
        
        num = min([len(flowvisors), len(mininet_vms)])
        
        self.mininet_vm_clients = []
        for i in xrange(num):
            client = SSHClient()
            client.set_missing_host_key_policy(AutoAddPolicy())
            client.connect(
                mininet_vms[i], username="mininet", password="mininet",
            )
            
            stdin, stdout, stderr = client.exec_command(
                "sudo mn --topo=%s --controller=remote "  % self.MININET_TOPO +
                "--ip=%s --port=%s --mac --switch=ovsk" % (
                    flowvisors[i]["host"], flowvisors[i]["of_port"],
                )
            )
            
            self.mininet_vm_clients.append((stdin, stdout, stderr, client))
        
    def clean_up_flowvisor(self, flowvisor):
        """
        Delete all the rules and slices.
        """
        import xmlrpclib, re
        id_re = re.compile(r"id=\[(?P<id>\d+)\]")
        s = xmlrpclib.ServerProxy(
            "https://%s:%s@%s:%s/xmlrpc" % (
                flowvisor["username"], flowvisor["password"],
                flowvisor["host"], flowvisor["xmlrpc_port"],
            )
        )
        flowspaces = s.api.listFlowSpace()
        ops = []
        for fs in flowspaces:
            id = id_re.search(fs).group("id")
            ops.append(dict(operation="REMOVE", id=id))
        if ops: s.api.changeFlowSpace(ops)
        
        slices = s.api.listSlices()
        [s.api.deleteSlice(slice) for slice in slices if slice != "root"]
        
        self.fv_client = s
        
    def prepare_om(self, proj_dir, flowvisor, ch_username, ch_passwd):
        """
        Flush the OM DB and add a flowvisor and user for the CH
        """
        from tests.commands import call_env_command, Env
        call_env_command(proj_dir, "flush",
                         interactive=False)
        self.om_env = Env(proj_dir)
        self.om_env.switch_to()
        
        from django.contrib.auth.models import User
        from optin_manager.users.models import UserProfile
        from optin_manager.xmlrpc_server.models import FVServerProxy
        
        # Create the clearinghouse user
        u = User.objects.create(username=ch_username)
        u.set_password(ch_passwd)
        u.save()
        profile = UserProfile.get_or_create_profile(u) 
        profile.is_clearinghouse_user = True
        profile.save()
        
        # Create the FV proxy connection
        FVServerProxy.objects.create(
            name="Flowvisor",
            username=flowvisor["username"],
            password=flowvisor["password"],
            url = "https://%s:%s/xmlrpc" % (
                flowvisor["host"], flowvisor["xmlrpc_port"],
            ),
        )
        self.om_env.switch_from()
        
    def prepare_ch(self, proj_dir, ch_host, ch_username, ch_passwd, 
                   om_host, om_port):
        """
        Flush and prepare the CH DB.
        Add the OMs to the CH.
        """
        from os.path import dirname
        proc = self.run_proc_cmd(
            "python %s/prepare_ch.py %s %s %s %s %s %s" % (
                dirname(__file__), proj_dir, ch_host, ch_username, ch_passwd, 
                om_host, om_port,
            )
        )
        proc.wait()
        out_data, err_data = proc.communicate()
        print out_data, err_data
        
    def run_proc_cmd(self, cmd):
        """
        Run a command in a subprocess, return the new process.
        """
        import shlex, subprocess
        args = shlex.split(cmd)
        return subprocess.Popen(args,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        
    def run_am_proxy(self, gcf_dir, ssl_dir, am_port):
        """
        Create the ssl certs for the tests.
        Run the AM proxy in a separate process.
        """
        from os.path import join
        import xmlrpclib

        # create the certs if not already there.
        self.run_proc_cmd("make -C %s" % ssl_dir).wait()
        
        # run the am
        self.am_proc = self.run_proc_cmd(
            "python %s -r %s -c %s -k %s -p %s" % (
                join(gcf_dir, "gam.py"), join(ssl_dir, "ca.crt"),
                join(ssl_dir, "server.crt"), join(ssl_dir, "server.key"),
                am_port,
            )
        )
        cert_transport = SafeTransportWithCert(
            keyfile=join(ssl_dir, "experimenter.key"),
            certfile=join(ssl_dir, "experimenter.crt"))
        self.am_client = xmlrpclib.ServerProxy(
            "https://localhost:%s/" % am_port,
            transport=cert_transport)

    def run_geni_ch(self, gcf_dir, ssl_dir, ch_port):
        from os.path import join
        import xmlrpclib

        self.ch_proc = self.run_proc_cmd(
            "python %s -r %s -c %s -k %s -p %s" % (
                join(gcf_dir, "gch.py"), join(ssl_dir, "ca.crt"),
                join(ssl_dir, "ch.crt"), join(ssl_dir, "ch.key"),
                ch_port,
            )
        )
        cert_transport = SafeTransportWithCert(
            keyfile=join(ssl_dir, "experimenter.key"),
            certfile=join(ssl_dir, "experimenter.crt"))
        self.ch_client = xmlrpclib.ServerProxy(
            "https://localhost:%s/" % ch_port,
            transport=cert_transport)
        
    def create_ch_slice(self):
        """
        Code mostly copied from GENI test harness from BBN.
        """
        import sfa.trust.credential as cred
        
        slice_cred_string = self.ch_client.CreateSlice()
        slice_credential = cred.Credential(string=slice_cred_string)
        slice_gid = slice_credential.get_gid_object()
        slice_urn = slice_gid.get_urn()
        
        # Set up the array of credentials as just the slice credential
        credentials = [slice_cred_string]
        
        return (slice_urn, credentials)

    def setUp(self):
        """
        Run dummy networks and connect them to the FVs
        Run dummy Controllers
        Load the configuration for the OM
        Load the configuration for the AM
        """
        import time
        from tests.gapi.helpers import kill_old_procs
        
        # clear all slices/flowspaces from fvs
        for flowvisor in test_settings.FLOWVISORS:
            self.clean_up_flowvisor(flowvisor)
            
        # Kill stale processes
        kill_old_procs(8000, 8001)
        
        ch_username = "clearinghouse"
        ch_passwd = "ch_password"
        
        # run experiment controllers
        self.run_nox(
            test_settings.MININET_VMS[0],
            test_settings.NUM_EXPERIMENTS,
            6633,
        )
        
        # connect the networks to FVs
        self.connect_networks(
            test_settings.FLOWVISORS,
            test_settings.MININET_VMS,
        )
        
        # setup the OM
        self.prepare_om(
            test_settings.OM_PROJECT_DIR,
            test_settings.FLOWVISORS[0],
            ch_username,
            ch_passwd,
        )
        
        time.sleep(4)
        
        # setup the CH (aka AM)
        self.prepare_ch(
            test_settings.CH_PROJECT_DIR,
            test_settings.HOST,
            ch_username,
            ch_passwd,
            test_settings.HOST,
            test_settings.OM_PORT,
        )
        
        # Run the AM proxy for GENI and the GENI clearinghouse
        self.run_geni_ch(test_settings.GCF_DIR, test_settings.SSL_DIR, 8000)
        self.run_am_proxy(test_settings.GCF_DIR, test_settings.SSL_DIR, 8001)
        
    def tearDown(self):
        """
        Clean up the Flowvisor rules/slices
        Clear running stuff and so on...
        """
        import time
        from tests.gapi.helpers import kill_old_procs

        # clear all slices/flowspaces from fvs
        for flowvisor in test_settings.FLOWVISORS:
            self.clean_up_flowvisor(flowvisor)
        
        
        # Kill stale processes
        kill_old_procs(8000, 8001)

        # kill ssh sessions
        for c in self.nox_clients:
            try:
                c[0].write("exit()\n")
            except:
                print "nox stdout %s" % c[1].read()
                print "nox stderr %s" % c[2].read()
            
        for c in self.mininet_vm_clients:
            try:
                c[0].write("exit()\n")
            except:
                print "mn stdout %s" % c[1].read()
                print "mn stderr %s" % c[2].read()
        
        time.sleep(4)
        
        for c in self.nox_clients:
            c[3].close()
            
        for c in self.mininet_vm_clients:
            c[3].close()

        time.sleep(2)

    def test_ListResources(self):
        """
        Check the list of resources.
        """
        from tests.gapi.helpers import parse_rspec
        
        slice_urn, cred = self.create_ch_slice()
        options = dict(geni_compressed=False, geni_available=True)
        rspec = self.am_client.ListResources(cred, options)
        
        print rspec
        
        # Create switches and links
        self.switches, self.links = parse_rspec(rspec)
        
        # check the number of switches and links
        self.assertEqual(len(self.switches), 2)
        self.assertEqual(len(self.links), 1)
        
    def test_CreateSliver(self):
        """
        Check that we can create slice on the FV
        """
        from tests.gapi.helpers import create_random_resv, parse_rspec
        
        # check no other slices
        slices = self.fv_client.api.listSlices()
        self.assertEqual(len(slices), 1) # root
        
        # get the resources
        slice_urn, cred = self.create_ch_slice()
        options = dict(geni_compressed=False, geni_available=True)
        rspec = self.am_client.ListResources(cred, options)
        
        # Create switches and links
        self.switches, self.links = parse_rspec(rspec)

        # create a random reservation
        slice_name = "SliceNameBla"
        email = "john.doe@geni.net"
        url = "tcp:%s:%s" % (test_settings.MININET_VMS[0], 6633)
        resv_rspec, flowspaces = create_random_resv(
            2, self.switches,
            slice_name=slice_name,
            email=email,
            ctrl_url=url,
        )
        self.am_client.CreateSliver(slice_urn, cred, resv_rspec)
        
        # TODO: check that the full reservation rspec is returned
        slices = self.fv_client.api.listSlices()
        self.assertEqual(len(slices), 2) # root + new slice
        
        # Check the name
        self.assertTrue(
            slice_name in slices[1], 
            "Expected to find %s in slice name %s, but didn't" % (
                slice_name, slices[1]
            )
        )
        
        # Check the slice information
        slice_info = self.fv_client.api.getSliceInfo(slices[1])
        print slice_info
        self.assertEqual(slice_info["contact_email"], email)
        self.assertEqual(slice_info["controller_port"], "6633")
        self.assertEqual(slice_info["controller_hostname"],
                         test_settings.MININET_VMS[0])

if __name__ == '__main__':
    import unittest
    unittest.main()
  
