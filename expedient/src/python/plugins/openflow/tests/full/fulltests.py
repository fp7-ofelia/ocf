'''
Created on May 17, 2010

@author: jnaous
'''
import sys
from os.path import join, dirname
import subprocess
import shlex
PYTHON_DIR = join(dirname(__file__), "../../../")
sys.path.append(PYTHON_DIR)

from unittest import TestCase
from expedient.common.utils.certtransport import SafeTransportWithCert
from expedient.common.tests.client import Browser
from openflow.tests import test_settings
import xmlrpclib, re
from openflow.tests.helpers import kill_old_procs, parse_rspec
from openflow.tests.helpers import create_random_resv
from expedient.common.tests.commands import call_env_command, Env
from expedient.common.tests.utils import drop_to_shell, wrap_xmlrpc_call

import logging
logger = logging.getLogger(__name__)

from helpers import SSHClientPlus

RUN_FV_SUBPROCESS = True
SCHEME = "https" if test_settings.USE_HTTPS else "http"

class FullIntegration(TestCase):
    MININET_TOPO = "tree,2"
    EXPECTED_NUM_SWITCHES = 3
    EXPECTED_NUM_LINKS = 4
    NOX_APPS = "pyswitch packetdump"

    def run_nox(self, mininet_vm, num, port_start):
        """
        Connect to the mininet_vm and run 'num' instances of nox as
        a pyswitch with packet dumping.
        """
        kill_client = SSHClientPlus.exec_command_plus(
            mininet_vm[0], "mininet", "mininet",
            "sudo kill `ps -ae | grep lt-nox_core | awk '{ print $1 }'`",
            port=mininet_vm[1],
        )
        kill_client.wait()
        
        self.nox_clients = []
        for i in xrange(num):
            port = port_start + i
            cmd = "cd noxcore/build/src; ./nox_core -i ptcp:%s %s" % (
                port, self.NOX_APPS,
            )
            client = SSHClientPlus.exec_command_plus(
                mininet_vm[0], "mininet", "mininet", cmd, port=mininet_vm[1],
            )

            self.nox_clients.append(client)
        
    def connect_networks(self, flowvisors, mininet_vms, switch="ovsk"):
        """
        Create a 2-switch, 2-host linear topology on each mininet vm
        Connect the switches to the FV.
        """
        num = min([len(flowvisors), len(mininet_vms)])
        
        self.mininet_vm_clients = []
        for i in xrange(num):
            logger.debug("Connecting to the mininet VM at %s:%s" % mininet_vms[i])
            cmd = "sudo mn --topo=%s "  % self.MININET_TOPO +\
                "--controller=remote --ip=%s --port=%s --mac --switch=%s" % (
                    flowvisors[i]["host"], flowvisors[i]["of_port"], switch,
                )
            client = SSHClientPlus.exec_command_plus(
                mininet_vms[i][0], "mininet", "mininet", cmd,
                port=mininet_vms[i][1],
            )
            self.mininet_vm_clients.append(client)
            logger.debug(
                client.wait_for_prompt(
                    prompt="Starting CLI:\n", timeout=test_settings.TIMEOUT))

    def run_flowvisor(self, flowvisor):
        """
        Run flowvisor.
        Delete all the rules and slices.
        """
        
        if RUN_FV_SUBPROCESS:
            kill_old_procs(flowvisor["of_port"],
                           flowvisor["xmlrpc_port"])

            self.fv_procs.append(
                self.run_proc_cmd(
                    "%s/scripts/flowvisor.sh %s/%s 2>&1 | tee /tmp/flowvisor.out " % (
                        flowvisor["path"][0], flowvisor["path"][0],
                        flowvisor["path"][1],
                    )
                )
            )
        
        id_re = re.compile(r"id=\[(?P<id>\d+)\]")
        fv_url = "https://%s:%s@%s:%s" % (
            flowvisor["username"], flowvisor["password"],
            flowvisor["host"], flowvisor["xmlrpc_port"],
        )

        s = xmlrpclib.ServerProxy(fv_url)
        
        logger.debug("Waiting for flowvisor to be up.")
        ret = wrap_xmlrpc_call(s.api.ping, ["PONG"], {}, test_settings.TIMEOUT)
        logger.debug("Ping returned: %s" % ret)
        
        logger.debug("Getting flowspace from flowvisor")
        flowspaces = s.api.listFlowSpace()
        ops = []
        logger.debug("Deleting all flowspace")
        for fs in flowspaces:
            id = id_re.search(fs).group("id")
            ops.append(dict(operation="REMOVE", id=id))
        if ops:
            s.api.changeFlowSpace(ops)
        
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
        from openflow.optin_manager.xmlrpc_server.ch_api import om_ch_translate
        from openflow.optin_manager.opts.models import AdminFlowSpace, UserFlowSpace
        import random
        
        # Create the Expedient user
        u = User.objects.create(username=ch_username)
        u.set_password(ch_passwd)
        u.save()
        profile = UserProfile.get_or_create_profile(u) 
        profile.is_clearinghouse_user = True
        profile.save()
        
        # make a normal user on system
        username = "user"
        password = "password"
        u = User.objects.create(username=username, is_active=True)
        u.set_password(password)
        u.save()

        # assign flowspace to the user
        random.seed(0)
        self.user_ip_src_s = random.randint(0,0x80000000) & 0xFFFF0000
        self.user_ip_src_e = random.randint(0x80000000,0xFFFFFFFF) & 0xFFFF0000
        fields=["dl_src","dl_dst","vlan_id","tp_src","tp_dst"]
        random.shuffle(fields)

        (to_str,from_str,width,om_name,of_name) = om_ch_translate.attr_funcs[fields[0]]
        self.user_field_name = om_name
        self.user_field_s = random.randint(0,2**(width)-3)
        self.user_field_e = self.user_field_s + 1

        # assign full flowspace to admin:
        username = "admin"
        password = "password"
        adm = User.objects.create(username=username, is_superuser=True,
                                  is_staff=True, is_active=True)
        adm.set_password(password)
        adm.save()
        profile = UserProfile.get_or_create_profile(adm) 
        profile.is_net_admin = True
        profile.supervisor = adm
        profile.max_priority_level = 7000
        profile.save()
        AdminFlowSpace.objects.create(user=adm)
        
        # assign flowspace to user
        ufs = UserFlowSpace(user=u, ip_src_s=self.user_ip_src_s,
                             ip_src_e=self.user_ip_src_e,approver=adm)
        setattr(ufs,"%s_s"%self.user_field_name,self.user_field_s)
        setattr(ufs,"%s_e"%self.user_field_name,self.user_field_e)
        ufs.save()     

        # Create the FV proxy connection
        fv = FVServerProxy(
            name="Flowvisor",
            username=flowvisor["username"],
            password=flowvisor["password"],
            url="https://%s:%s/xmlrpc" % (
                flowvisor["host"], flowvisor["xmlrpc_port"],
            ),
            verify_certs=False,
        )
        fv.save()
        
        self.om_client = xmlrpclib.ServerProxy(
            SCHEME+"://%s:%s@%s:%s/xmlrpc/xmlrpc/" % (
                ch_username, ch_passwd,
                test_settings.HOST, test_settings.OM_PORT,
            )
        )
        
        self.om_env.switch_from()
        
    def prepare_ch(self, proj_dir, ch_host, ch_port, ch_username, ch_passwd, 
                   om_host, om_port):
        """
        Flush and prepare the CH DB.
        Add the OMs to the CH.
        """
        from os.path import dirname
        
        subprocess.call(shlex.split(
            "python %s/manage.py flush --noinput" % proj_dir))
        subprocess.call(shlex.split(
            "python %s/manage.py syncdb --noinput" % proj_dir))
        subprocess.call(shlex.split(
            "python %s/manage.py createsuperuser --noinput "
            "--username=expedient --email=bla@bla.com"  % proj_dir))
        subprocess.call(shlex.split(
            "python %s/manage.py set_fake_passwords"
            " --password=expedient"  % proj_dir))

        browser = Browser()
        browser.login(
            SCHEME+"://%s:%s%s" % (
                ch_host, ch_port, "/accounts/login/"),
            "expedient", "expedient")
        response = browser.get_and_post_form(
            url=SCHEME+"://%s:%s%s" % (
                ch_host, ch_port, "/openflow/aggregate/create/"),
            params=dict(
                name="Test OM",
                description="TestOM Description",
                location="Stanford, CA",
                usage_agreement="Do you agree?",
                username=ch_username,
                password=ch_passwd,
                url=SCHEME+"://%s:%s%s" % (
                    om_host, om_port, "/xmlrpc/xmlrpc/"),
            ),
            del_params=["verify_certs"],
        )
        self.assertTrue(
            response.geturl() == \
                SCHEME+"://%s:%s%s" % (
                    ch_host, ch_port, "/openflow/aggregate/1/links/"),
            "Did not redirect after create correctly. Response was: %s"
            % response.read(),
        )
        
    def run_proc_cmd(self, cmd, wait=False):
        """
        Run a command in a subprocess, return the new process.
        """
        if test_settings.SHOW_PROCESSES_IN_XTERM:
            from expedient.common.tests.utils import run_cmd_in_xterm as run_cmd
        else:
            from expedient.common.tests.utils import run_cmd
            
        if wait:
            return run_cmd(cmd).wait()
        else:
            return run_cmd(cmd)
        
    def run_am_proxy(self, gcf_dir, ssl_dir, am_port, ch_host, ch_port):
        """
        Create the ssl certs for the tests.
        Run the AM proxy in a separate process.
        """

        # create the certs if not already there.
        self.run_proc_cmd("make -C %s" % ssl_dir).wait()
        
        # run the am
#        self.am_proc = self.run_proc_cmd(
#            "python %s -r %s -c %s -k %s -p %s -u %s --debug -H 0.0.0.0" % (
#                join(gcf_dir, "gam.py"), join(ssl_dir, "certs"),
#                join(ssl_dir, "server.crt"), join(ssl_dir, "server.key"),
#                am_port,
#                SCHEME + "://%s:%s/openflow/gapi/"
#                % (ch_host, ch_port),
#            )
#        )
        cert_transport = SafeTransportWithCert(
            keyfile=join(ssl_dir, "experimenter.key"),
            certfile=join(ssl_dir, "experimenter.crt"))
        self.am_client = xmlrpclib.ServerProxy(
            "https://%s:%s/openflow/gapi/" % (test_settings.HOST, am_port),
            transport=cert_transport)
        
    def run_geni_ch(self, gcf_dir, ssl_dir, ch_port):
        """
        Run the GENI Sample CH in a subprocess and connect to it.
        """
        self.ch_proc = self.run_proc_cmd(
            "python %s -u %s -r %s -c %s -k %s -p %s --debug -H 0.0.0.0" % (
                join(gcf_dir, "gch.py"),
                join(ssl_dir, "experimenter.crt"),
                join(ssl_dir, "certs"),
                join(ssl_dir, "ch.crt"), join(ssl_dir, "ch.key"),
                ch_port,
            )
        )
        cert_transport = SafeTransportWithCert(
            keyfile=join(ssl_dir, "experimenter.key"),
            certfile=join(ssl_dir, "experimenter.crt"))
        self.ch_client = xmlrpclib.ServerProxy(
            "https://%s:%s/" % (test_settings.HOST, ch_port),
            transport=cert_transport)

    def create_ch_slice(self):
        """
        Code mostly copied from GENI test harness from BBN.
        """
        import gcf.sfa.trust.credential as cred
        
        slice_cred_string = wrap_xmlrpc_call(
            self.ch_client.CreateSlice, [], {}, test_settings.TIMEOUT)
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
        # Kill stale processes
        kill_old_procs(test_settings.GAM_PORT, test_settings.GCH_PORT)
        
        self.ch_username = "clearinghouse"
        self.ch_passwd = "ch_password"

        # clear all slices/flowspaces from fvs
        self.fv_procs = []
        self.fv_clients = []
        for flowvisor in test_settings.FLOWVISORS:
            self.run_flowvisor(flowvisor)
        
#        # run experiment controllers
#        self.run_nox(
#            test_settings.MININET_VMS[0][0],
#            test_settings.NUM_EXPERIMENTS,
#            6633,
#        )
        
        # connect the networks to FVs
        self.connect_networks(
            test_settings.FLOWVISORS,
            test_settings.MININET_VMS,
            test_settings.MININET_SWITCH_TYPE,
        )
        
        # setup the OM
        self.prepare_om(
            test_settings.OM_PROJECT_DIR,
            test_settings.FLOWVISORS[0],
            self.ch_username,
            self.ch_passwd,
        )
        
        # setup Expedient (aka AM)
        self.prepare_ch(
            test_settings.CH_PROJECT_DIR,
            test_settings.HOST,
            test_settings.CH_PORT,
            self.ch_username,
            self.ch_passwd,
            test_settings.HOST,
            test_settings.OM_PORT,
        )

        # store the trusted CA dir
        import os
        from django.conf import settings as djangosettings
        self.before = os.listdir(djangosettings.XMLRPC_TRUSTED_CA_PATH)

        # Run the AM proxy for GENI and Expedient
        self.run_geni_ch(
            test_settings.GCF_DIR, test_settings.SSL_DIR, test_settings.GAM_PORT)
        self.run_am_proxy(
            test_settings.GCF_DIR, test_settings.SSL_DIR, test_settings.GCH_PORT,
            test_settings.HOST, test_settings.CH_PORT)
        
    def tearDown(self):
        """
        Clean up the Flowvisor rules/slices
        Clear running stuff and so on...
        """
        # restore the trusted CA dir
        from django.conf import settings as djangosettings
        import os
        after = os.listdir(djangosettings.XMLRPC_TRUSTED_CA_PATH)
        for path in after:
            if path not in self.before:
                os.unlink(os.path.join(djangosettings.XMLRPC_TRUSTED_CA_PATH, path))

        if test_settings.PAUSE_AFTER_TESTS:
            raw_input("Press ENTER to continue:")
            
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
#        for c in self.nox_clients:
#            out = c.communicate("\03", check_closed=True)
#            logger.debug("nox stdout %s" % out)
            
        for c in self.mininet_vm_clients:
            out = c.communicate("exit()\n", check_closed=True)
            logger.debug("mn stdout %s" % out)
            c.wait()
        
        if RUN_FV_SUBPROCESS:
            for flowvisor in test_settings.FLOWVISORS:
                kill_old_procs(flowvisor["of_port"], flowvisor["xmlrpc_port"])
        
        # Kill stale processes
        kill_old_procs(test_settings.GAM_PORT, test_settings.GCH_PORT)

#        for c in self.nox_clients:
#            try:
#                c.close()
#            except:
#                pass

        for c in self.fv_procs:
            try:
                c.close()
            except:
                pass

            
        for c in self.mininet_vm_clients:
            try:
                c.close()
            except:
                pass

    def create_sliver_core(self,fs_randomness):
        """
        Check that we can create slice on the FV
        """
        # check no other slices
        slices = self.fv_clients[0].api.listSlices()
        self.assertEqual(len(slices), 1) # root
        
        # get the resources
        slice_urn, cred = self.test_ListResources()
        
        # create a random reservation
        slice_name = "SliceNameBla"
        email = "john.doe@geni.net"
        url = "tcp:%s:%s" % (test_settings.MININET_VMS[0][0], 6633)
        resv_rspec, flowspaces = create_random_resv(
            2, self.switches,
            slice_name=slice_name,
            email=email,
            ctrl_url=url,
            fs_randomness = fs_randomness,
        )
        users = [{'key':''}]
        self.am_client.CreateSliver(slice_urn, cred, resv_rspec, users)
        
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
        logger.debug("Slice info is %s" % slice_info)
        self.assertEqual(slice_info["contact_email"], email)
        self.assertEqual(slice_info["controller_port"], "6633")
        self.assertEqual(slice_info["controller_hostname"],
                         test_settings.MININET_VMS[0][0])
        
        return (slice_urn, cred)

    def test_GetVersion(self):
        ret = wrap_xmlrpc_call(
            self.am_client.GetVersion, [], {}, test_settings.TIMEOUT)
        self.assertEqual(ret['geni_api'], 1)
    

    def test_ListResources(self):
        """
        Check the list of resources.
        """

        # check the switches on the FV
        devices = self.fv_clients[0].api.listDevices()
        logger.debug("FV devices: %s" % devices)
        self.assertEqual(len(set(devices)), self.EXPECTED_NUM_SWITCHES)
        
        slice_urn, cred = self.create_ch_slice()
        options = dict(geni_compressed=False, geni_available=True)
        rspec = wrap_xmlrpc_call(
            self.am_client.ListResources, [cred, options], {}, 
            test_settings.TIMEOUT)
        
        logger.debug(rspec)
        
        # Create switches and links
        self.switches, self.links = parse_rspec(rspec)
        
        # check the number of switches and links
        self.assertEqual(len(self.switches), self.EXPECTED_NUM_SWITCHES)
        self.assertEqual(len(self.links), self.EXPECTED_NUM_LINKS)
        return slice_urn, cred
        
    def test_CreateSliver(self):
        """
        Check that we can create slice on the FV
        """
        return self.create_sliver_core(fs_randomness=True)
        

    def test_CreateDeleteSliver(self):
        """
        Check that we can create then delete a sliver.
        """
        slice_urn, cred = self.test_CreateSliver()
        
        self.assertTrue(
            wrap_xmlrpc_call(
                self.am_client.DeleteSliver,
                [slice_urn, cred], {}, 
                test_settings.TIMEOUT),
            "Failed to delete sliver.")
        
        self.assertEqual(
            len(self.fv_clients[0].api.listSlices()),
            1,
            "Slice not deleted at FlowVisor",
        )
        
    def test_UserOptIn1(self):
        """
        Test a user opting in.
        """
        from expedient.common.tests.client import Browser
        
        #create an experiment through CH
        self.create_sliver_core(fs_randomness=False)
        
        logger.debug("Done creating sliver")

        # Get user to opt in
        logger.debug("Logging into browser")
        b = Browser()
        logged_in = b.login(SCHEME+"://%s:%s/accounts/login/"%
                            (test_settings.HOST, test_settings.OM_PORT),
                            "user","password")
        self.assertTrue(logged_in,"Could not log in")
        logger.debug("Login success")
#        drop_to_shell(local=locals())

        f = b.get_and_post_form(SCHEME+"://%s:%s/opts/opt_in"%
                                (test_settings.HOST, test_settings.OM_PORT),
                                dict(experiment=1))
        logger.debug("Posted opt-in request, reading response.")
        res = f.read()
        self.assertEqual(f.code, 200)
        self.assertTrue("successfully" in res, "Did not get successful opt in message: %s" % res)
        
        
        # test if FV has the expected flowspace match entries
        from expedient.common.tests.utils import run_cmd
        fvctl = run_cmd(
            "sh %s/scripts/fvctl.sh listFlowSpace" % (
                test_settings.FLOWVISOR_DIR,
            ),
        )
        data = fvctl.communicate(input="rootpassword")
        fv_rules = data[0].split("\n")
        print(fv_rules)
        #for fv_rule in fv_rules
        
        logger.debug("Response fine, opting out.")
        # now test opt out:
        f = b.get_and_post_form(SCHEME+"://%s:%s/opts/opt_out"%
                                (test_settings.HOST, test_settings.OM_PORT),
                                {"1":"checked"})
        res = f.read()
        self.assertEqual(f.code, 200)
        self.assertTrue("Successful" in res, "Returned %s"%res)        
        
    def test_UserOptIn2(self):
        """
        Test a user opting in.
        """
        from expedient.common.tests.client import Browser
        from openflow.optin_manager.opts.models import Experiment,ExperimentFLowSpace
        import random
                
        slices = self.fv_clients[0].api.listSlices()
        self.assertEqual(len(slices), 1) # root
        
        # get the resources
        slice_urn, cred = self.create_ch_slice()
        options = dict(geni_compressed=False, geni_available=True)
        rspec = self.am_client.ListResources(cred, options)
        
        # Create switches and links
        switches, links = parse_rspec(rspec)
        
        exp = Experiment.objects.create(slice_id="slice_id", project_name="project name",
                      project_desc="project description", slice_name="slice name",
                      slice_desc="slice description", controller_url="controller url",
                      owner_email="owner email", owner_password="owner password")
            
        for switch in switches:
            exp_ip_src_s = random.randint(0,0x80000000) & 0xFFFF0000
            exp_ip_src_e = random.randint(0x80000000,0xFFFFFFFF) & 0xFFFF0000
            ExperimentFLowSpace.objects.create(exp=exp, dpid=switch.dpid,
                            ip_src_s=exp_ip_src_s, 
                            ip_src_e=exp_ip_src_e, 
                             )

        logger.debug("Done creating sliver")

        # Get user to opt in
        logger.debug("Logging into browser")
        b = Browser()
        logged_in = b.login(SCHEME+"://%s:%s/accounts/login/"%
                            (test_settings.HOST, test_settings.OM_PORT),
                            "user","password")
        self.assertTrue(logged_in,"Could not log in")
        logger.debug("Login success")
#        drop_to_shell(local=locals())

        f = b.get_and_post_form(SCHEME+"://%s:%s/opts/opt_in"%
                                (test_settings.HOST, test_settings.OM_PORT),
                                dict(experiment=1))
        logger.debug("Posted opt-in request, reading response.")
        res = f.read()
        self.assertEqual(f.code, 200)
        self.assertTrue("successfully" in res, "Did not get successful opt in message: %s" % res)
        
        logger.debug("Response fine, opting out.")
        # now test opt out:
        f = b.get_and_post_form(SCHEME+"://%s:%s/opts/opt_out"%
                                (test_settings.HOST, test_settings.OM_PORT),
                                {"1":"checked"})
        res = f.read()
        self.assertEqual(f.code, 200)
        self.assertTrue("Successful" in res, "Returned %s"%res)

if __name__ == '__main__':
    import unittest
    unittest.main()
  
