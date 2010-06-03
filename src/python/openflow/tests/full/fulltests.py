'''
Created on May 17, 2010

@author: jnaous
'''
from unittest import TestCase
from expedient.common.utils.certtransport import SafeTransportWithCert
from openflow.tests import test_settings
from helpers import SSHClientPlus
import xmlrpclib, re
from openflow.tests.helpers import kill_old_procs, parse_rspec, Flowspace
from openflow.tests.helpers import create_random_resv
import time
from expedient.common.tests.commands import call_env_command, Env
from os.path import join
from expedient.clearinghouse.loggingconf import getLogger

logger = getLogger(__name__)

# TODO: Some of this code works with multiple FVs, other parts assume only one.

RUN_FV_SUBPROCESS = False

class FullIntegration(TestCase):
    MININET_TOPO = "linear,2"
    NOX_APPS = "pyswitch packetdump"
    
    def run_nox(self, mininet_vm, num, port_start):
        """
        Connect to the mininet_vm and run 'num' instances of nox as
        a pyswitch with packet dumping.
        """
        kill_client = SSHClientPlus.exec_command_plus(
            mininet_vm, "mininet", "mininet",
            "sudo kill `ps -ae | grep lt-nox_core | awk '{ print $1 }'`"
        )
        kill_client.wait()
        time.sleep(2)
        
        self.nox_clients = []
        for i in xrange(num):
            port = port_start + i
            cmd = "cd noxcore/build/src; ./nox_core -i ptcp:%s %s" % (
                port, self.NOX_APPS,
            )
            client = SSHClientPlus.exec_command_plus(
                mininet_vm, "mininet", "mininet", cmd
            )
            time.sleep(2)
            logger.debug("Communicating with nox client run on port %s" % port)
            out = client.communicate()
            logger.debug("Client out:\n%s" % out)

            self.nox_clients.append(client)
        
    def connect_networks(self, flowvisors, mininet_vms):
        """
        Create a 2-switch, 2-host linear topology on each mininet vm
        Connect the switches to the FV.
        """
        num = min([len(flowvisors), len(mininet_vms)])
        
        self.mininet_vm_clients = []
        for i in xrange(num):
            cmd = "sudo mn --topo=%s "  % self.MININET_TOPO +\
                "--controller=remote --ip=%s --port=%s --mac --switch=ovsk" % (
                    flowvisors[i]["host"], flowvisors[i]["of_port"],
                )
            client = SSHClientPlus.exec_command_plus(
                mininet_vms[i], "mininet", "mininet", cmd,
            )
            self.mininet_vm_clients.append(client)

            time.sleep(2)

            logger.debug("Communicating with mininet client")
            out = client.communicate()
            logger.debug("Client out:\n%s" % out)
        
    def run_flowvisor(self, flowvisor):
        """
        Run flowvisor.
        Delete all the rules and slices.
        """
        
        if RUN_FV_SUBPROCESS:
            kill_old_procs(flowvisor["of_port"],
                           flowvisor["xmlrpc_port"])
            time.sleep(2)
            self.fv_procs.append(
                self.run_proc_cmd(
                    "%s/scripts/flowvisor.sh %s/%s" % (
                        flowvisor["path"][0], flowvisor["path"][0],
                        flowvisor["path"][1],
                    )
                )
            )
            # wait for flowvisor to be up
            time.sleep(2)
        
        id_re = re.compile(r"id=\[(?P<id>\d+)\]")
        s = xmlrpclib.ServerProxy(
            "https://%s:%s@%s:%s" % (
                flowvisor["username"], flowvisor["password"],
                flowvisor["host"], flowvisor["xmlrpc_port"],
            )
        )
        logger.info("Getting flowspace from flowvisor")
        flowspaces = s.api.listFlowSpace()
        ops = []
        logger.info("Deleting all flowspace")
        for fs in flowspaces:
            id = id_re.search(fs).group("id")
            ops.append(dict(operation="REMOVE", id=id))
        if ops: s.api.changeFlowSpace(ops)
        
        slices = s.api.listSlices()
        [s.api.deleteSlice(slice) for slice in slices if slice != "root"]
        
        self.fv_clients.append(s)
        
    def prepare_om(self, proj_dir, flowvisor, ch_username, ch_passwd):
        """
        Flush the OM DB and add a flowvisor and user for the CH
        """
        call_env_command(proj_dir, "flush",
                         interactive=False)
        self.om_env = Env(proj_dir)
        self.om_env.switch_to()
        
        from django.contrib.auth.models import User
        from openflow.optin_manager.users.models import UserProfile
        from openflow.optin_manager.xmlrpc_server.models import FVServerProxy
        
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
        
        self.om_client = xmlrpclib.ServerProxy(
            "https://%s:%s@%s:%s/xmlrpc/xmlrpc/" % (
                ch_username, ch_passwd,
                test_settings.HOST, test_settings.OM_PORT,
            )
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
        logger.debug(out_data)
        logger.debug(err_data)
        
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
        
        time.sleep(2)

    def run_geni_ch(self, gcf_dir, ssl_dir, ch_port):
        """
        Run the GENI Sample CH in a subprocess and connect to it.
        """
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

        time.sleep(2)

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
        Run dummy networks and connect them to the FVs
        Run dummy Controllers
        Load the configuration for the OM
        Load the configuration for the AM
        """
        # clear all slices/flowspaces from fvs
        self.fv_procs = []
        self.fv_clients = []
        for flowvisor in test_settings.FLOWVISORS:
            self.run_flowvisor(flowvisor)
            
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
        
        time.sleep(2)
        
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
        # clear all slices/flowspaces from fvs
        if RUN_FV_SUBPROCESS:
            for fv_proc in self.fv_procs:
                try:
                    fv_proc.terminate()
                except:
                    pass
        
        self.am_proc.terminate()
        self.ch_proc.terminate()
        
        # kill ssh sessions
        for c in self.nox_clients:
            out = c.communicate("\03", check_closed=True)
            logger.debug("nox stdout %s" % out)
            
        for c in self.mininet_vm_clients:
            out = c.communicate("exit()\n", check_closed=True)
            logger.debug("mn stdout %s" % out)
        
        time.sleep(5)

        if RUN_FV_SUBPROCESS:
            for flowvisor in test_settings.FLOWVISORS:
                kill_old_procs(flowvisor["of_port"], flowvisor["xmlrpc_port"])
        
        # Kill stale processes
        kill_old_procs(8000, 8001)

        for c in self.nox_clients:
            try:
                c.close()
            except:
                pass
            
        for c in self.mininet_vm_clients:
            try:
                c.close()
            except:
                pass

    def test_ListResources(self):
        """
        Check the list of resources.
        """
        slice_urn, cred = self.create_ch_slice()
        options = dict(geni_compressed=False, geni_available=True)
        rspec = self.am_client.ListResources(cred, options)
        
        logger.debug(rspec)
        
        # Create switches and links
        self.switches, self.links = parse_rspec(rspec)
        
        # check the number of switches and links
        self.assertEqual(len(self.switches), 2)
        self.assertEqual(len(self.links), 2)
        
    def test_createSlice(self):
        """
        Test that the om calls the FV correctly.
        """
        f = Flowspace({"dl_dst": ("*", "*")},
                      ["00:11:22:33:aa:bb:cc:dd"])
        
        attrs = f.get_full_attrs()
        # create some random flowspaces
        switch_slivers=[{"datapathid": "00:11:22:33:aa:bb:cc:dd",
                         "flowspace": [attrs],
                         }]

        args = {
            "slice_id": "slice_id",
            "project_name": "project_name",
            "project_description": "project_description",
            "slice_name": "slice name-slice_id",
            "slice_description": "slice_description",
            "controller_url": "tcp:bla.bla.bla:6633",
            "owner_email": "bla@bla.com",
            "owner_password": "password",
            "switch_slivers": switch_slivers,
        }
        
        # Create!
        ret = self.om_client.create_slice(
            args["slice_id"], args["project_name"], args["project_description"],
            args["slice_name"], args["slice_description"],
            args["controller_url"], args["owner_email"], args["owner_password"],
            args["switch_slivers"]
        )
        
        self.assertTrue(ret)
        
        slices = self.fv_clients[0].api.listSlices()
        self.assertEqual(len(slices), 2)
        
        if slices[0] == "root":
            slice = slices[1]
        else:
            slice = slices[0]
            
        # TODO: Fix this test after Rob fixes escaping bug
        self.assertEqual(
            slice, "%s ID: %s" % (
                args["slice_name"].replace(".", "_"),
                args["slice_id"].replace(".", "_"),
            )
        )
        
        slice_info = self.fv_clients[0].api.getSliceInfo(slice)
        self.assertEqual(slice_info["contact_email"], args["owner_email"])
        self.assertEqual(slice_info["controller_port"], "6633")
        self.assertEqual(slice_info["controller_hostname"], "bla.bla.bla")
        
    def test_CreateSliver(self):
        """
        Check that we can create slice on the FV
        """
        # check no other slices
        slices = self.fv_clients[0].api.listSlices()
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
        slices = self.fv_clients[0].api.listSlices()
        logger.debug(slices)

        self.assertEqual(len(slices), 2) # root + new slice
        
        fv_slice_name = slices[1] if slices[0] == "root" else slices[0]
        
        # Check the name
        self.assertTrue(
            slice_name in fv_slice_name, 
            "Expected to find '%s' in slice name '%s', but didn't" % (
                slice_name, fv_slice_name,
            )
        )
        
        # Check the slice information
        slice_info = self.fv_clients[0].api.getSliceInfo(fv_slice_name)
        logger.debug(slice_info)
        self.assertEqual(slice_info["contact_email"], email)
        self.assertEqual(slice_info["controller_port"], "6633")
        self.assertEqual(slice_info["controller_hostname"],
                         test_settings.MININET_VMS[0])
        
        return (slice_urn, cred)

    def test_CreateDeleteSliver(self):
        """
        Check that we can create then delete a sliver.
        """
        slice_urn, cred = self.test_CreateSliver()
        
        self.assertTrue(
            self.am_client.DeleteSliver(slice_urn, cred),
            "Failed to delete sliver.")
        
        self.assertEqual(
            len(self.fv_clients[0].api.listSlices()),
            1,
            "Slice not deleted at FlowVisor",
        )

if __name__ == '__main__':
    import unittest
    unittest.main()
  
