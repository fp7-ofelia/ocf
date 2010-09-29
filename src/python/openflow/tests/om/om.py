'''
Created on May 15, 2010

@author: jnaous
'''
import sys
from os.path import dirname, join
SRC_DIR = join(dirname(__file__), '../../../')
sys.path.append(SRC_DIR)

from unittest import TestCase
from expedient.common.tests.commands import call_env_command, Env
from openflow.tests import test_settings
from expedient.common.tests.utils import wrap_xmlrpc_call
import xmlrpclib
import random
from pprint import pprint
import logging

logger = logging.getLogger("om_test")

SCHEME = "https" if test_settings.USE_HTTPS else "http"

class OMTests(TestCase):
    
    def setUp(self):
        """
        Load up a DB for the OM.
        Create a client to talk to the OM.
        """
        
        
        call_env_command(test_settings.OM_PROJECT_DIR, "flush",
                         interactive=False)
        self.om_env = Env(test_settings.OM_PROJECT_DIR)
        self.om_env.switch_to()
        
        from openflow.optin_manager.dummyfv.models import DummyFV
        from openflow.optin_manager.xmlrpc_server.models import FVServerProxy
        from openflow.optin_manager.users.models import UserProfile
        from django.contrib.auth.models import User 

        # Create the Expedient user
        username = "clearinghouse"
        password = "password"
        u = User.objects.create(username=username)
        u.set_password(password)
        u.save()
        
        profile = UserProfile.get_or_create_profile(u) 
        profile.is_Expedient_user = True
        profile.save()
        self.om_client = xmlrpclib.ServerProxy(
            SCHEME + "://%s:%s@%s:%s/xmlrpc/xmlrpc/" % (
                username, password, test_settings.HOST, test_settings.OM_PORT
            )
        )
        
        #creat admin user: use this to look at DBs through admin interface
        username = "admin"
        password = "password"
        u = User.objects.create(username=username, is_superuser=True,
                                is_staff=True, is_active=True)
        u.set_password(password)
        u.save()
        profile = UserProfile.get_or_create_profile(u) 
        profile.is_net_admin = True
        profile.supervisor = u
        profile.max_priority_level = 7000
        profile.save()      
         
         
        # Create dummy FVs
        for i in range(test_settings.NUM_DUMMY_FVS):
            fv = DummyFV.objects.create()
            # Load up a fake topology in the Dummy FV
            fv.populateTopology(10, 20, use_random=test_settings.USE_RANDOM)
            
            # create fake users for the Dummy FV
            username = "om%s" % i
            password = "password"
            u = User.objects.create(username=username)
            u.set_password(password)
            u.save()

            # Create the FV proxy connection
            FVServerProxy.objects.create(
                name="Flowvisor %s" % i,
                username=username,
                password=password,
                url = SCHEME+"://%s:%s/dummyfv/%s/xmlrpc/" % (
                    test_settings.HOST, test_settings.OM_PORT, fv.id,
                ),
            )
             
 
    def test_ping(self):
        """
        Communications are up.
        """
        ret = wrap_xmlrpc_call(
            self.om_client.ping, ["PING"], {}, test_settings.TIMEOUT)
        self.assertEqual(ret, "PONG: PING", "Ping returned %s." % ret)
        
    def test_get_switches(self):
        """
        Test that a slice can be created and the calls are routed to the
        FV correctly.
        """
        from openflow.optin_manager.dummyfv.models import DummyFVDevice

        # TODO: Fix to also check the returned info
        self.dpids_info = wrap_xmlrpc_call(
            self.om_client.get_switches, [], {}, test_settings.TIMEOUT)
        dpids = set([d[0] for d in self.dpids_info])
        
        # check that we expect all the dpids
        expected = set(
            DummyFVDevice.objects.values_list('dpid', flat=True),
        )
        
        self.assertEqual(
            dpids, expected, 
            "Received dpids (%s) not same as expected (%s)." % (
                dpids, expected,
            )
        )
        
    def test_get_links(self):
        """
        Tests that the links are retrieved correctly from the FV.
        """
        from openflow.optin_manager.dummyfv.models import DummyFVLink

        links = wrap_xmlrpc_call(
            self.om_client.get_links, [], {}, test_settings.TIMEOUT)
        links = set([tuple(l[:-1]) for l in links])
#        print "Received links:"
#        pprint(links)
        
        # TODO add checking for the link_infos (link attributes)
        
        expected = set([(
            link.src_dev.dpid,
            link.src_port,
            link.dst_dev.dpid,
            link.dst_port) for link in DummyFVLink.objects.all()])
#        print "Expected links:"
#        pprint(expected)
        
        self.assertTrue(
            links.issubset(expected),
            "Received links have %s not in expected links" % (
                links - expected,
            )
        )
        self.assertTrue(
            expected.issubset(links),
            "Expected links have %s not in received links" % (
                expected - links,
            )
        )
        
    def test_change_password(self):
        """
        Tests that the Expedient password can be changed correctly.
        """
        from django.contrib.auth.models import User
        wrap_xmlrpc_call(
            self.om_client.change_password, ["new_password"], {},
            test_settings.TIMEOUT)
        
        user = User.objects.get(username="clearinghouse")
        
        self.assertTrue(user.check_password("new_password"))
        
    
    def test_topology_callback(self):
        # TODO: write up test_topology_callback
        pass
    
    def test_create_slice(self, id=10):
        """
        Tests that slices are created correctly from the OM to the FV
        """
        from openflow.tests.helpers import Flowspace
        from openflow.optin_manager.dummyfv.models import DummyFV, DummyFVRule
        from openflow.optin_manager.dummyfv.models import DummyFVSlice
        from openflow.optin_manager.opts.models import Experiment
        from openflow.optin_manager.opts.models import ExperimentFLowSpace
        from openflow.optin_manager.xmlrpc_server.ch_api import convert_star_int
        
        # get the switches into self.dpids_info
        self.test_get_switches()
        
        # create some random flowspaces
        switch_slivers=[]
        for i in xrange(10):
            switch = random.choice(self.dpids_info)
#            print "Creating flow space for switch %s" % switch
            fs_set = [Flowspace.create_random([switch]) \
                      for j in range(random.randint(1,10))]
            switch_slivers.append({
                "datapath_id": switch[0],
                "flowspace": [fs.get_full_attrs() for fs in fs_set],
            })
        
        args = {
            "slice_id": id,
            "project_name": "project_name",
            "project_description": "project_description",
            "slice_name": "slice name-%s" % id,
            "slice_description": "slice_description",
            "controller_url": "bla:bla.bla.bla:6633",
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
        
        # check the return value
        self.assertEqual(ret, {'error_msg': "", 'switches': []})
        
        # check the OM database to see if Experiment has been created correctly

        returned = Experiment.objects.filter(slice_name=args["slice_name"])
        self.assertEqual(
            returned.count(), 1 ,
            "more than one slice with same name %s" % args["slice_name"])
        returned_string = "%s %s %s %s %s %s %s %s" % (
            returned[0].slice_id, returned[0].slice_name,
            returned[0].slice_desc, returned[0].project_name,
            returned[0].project_desc, returned[0].controller_url,
            returned[0].owner_email, returned[0].owner_password
        )
        expected_string = "%s %s %s %s %s %s %s %s" % ( 
            args["slice_id"],args["slice_name"],
            args["slice_description"],args["project_name"],
            args["project_description"],args["controller_url"],
            args["owner_email"],args["owner_password"])

        self.assertEqual(
            returned_string, expected_string,
            "The OM Experiment table is different " + \
            "from what expected %s != %s" % (returned_string,expected_string)
        )
        
        # check the OM database to see if ExperimentFlowSpace 
        # has been created correctly
        expfs = ExperimentFLowSpace.objects.filter(exp=returned[0])
        returned_string = ""
        for fs in expfs:
            returned_string = "%s %s %s %s %s " % (
                returned_string, fs.dpid, fs.port_number_s, fs.port_number_e,
                fs.stringify()
            )
        expected_string = ""

        for sliver in args["switch_slivers"]:
            for fs in sliver["flowspace"]:
                fs = convert_star_int(fs)
                expected_string = \
                    "%s %s %s %s %s %s %s %s %s %s %s " % (
                        expected_string, sliver["datapath_id"],
                        fs["port_num_start"], fs["port_num_end"],
                        fs["dl_src_start"], fs["dl_src_end"],
                        fs["dl_dst_start"], fs["dl_dst_end"],
                        fs["vlan_id_start"], fs["vlan_id_end"],
                        fs["nw_src_start"],
                    ) +\
                    "%s %s %s %s %s %s %s %s %s " % (
                        fs["nw_src_end"], fs["nw_dst_start"], fs["nw_dst_end"],
                        fs["nw_proto_start"], fs["nw_proto_end"],
                        fs["tp_src_start"], fs["tp_src_end"],
                        fs["tp_dst_start"], fs["tp_dst_end"]
                    )

        self.assertEqual(
            returned_string, expected_string,
            "Experiment FlowSpaces are not equal %s != %s" % (
                returned_string,expected_string
            )
        )

        for fv in DummyFV.objects.all():
#            DummyFVSlice.objects.get(
#                name="%s ID: %s" % (args["slice_name"], args["slice_id"]),
#                password=args["owner_password"],
#                controller_url=args["controller_url"],
#                email=args["owner_email"],
#                fv=fv,
#            )
            self.assertEqual(DummyFVRule.objects.filter(fv=fv).count(), 0)

    def test_delete_slice(self):
        """
        Tests that slices are deleted correctly from the OM to FV
        """
        from openflow.optin_manager.dummyfv.models import DummyFV, DummyFVSlice
        from openflow.optin_manager.opts.models import Experiment, \
            ExperimentFLowSpace

        num_slices = random.randint(1, 5)
        for i in range(num_slices):
            self.test_create_slice(id=i)
        
        # delete some slices and make sure they are gone
        ids = range(1, num_slices)
        random.shuffle(ids)
        for i in ids:
            err = wrap_xmlrpc_call(
                self.om_client.delete_slice, [i], {}, test_settings.TIMEOUT)
            self.assertEqual(err, "")
            num_slices -= 1
            for fv in DummyFV.objects.all():
                num_actual_slices = DummyFVSlice.objects.filter(fv=fv).count()
                self.assertTrue(
                    num_actual_slices == num_slices,
                    "Expected %s slices after delete but found %s" % (
                        num_slices, num_actual_slices))
            # Check internal OM database:
            count = Experiment.objects.all().count()
            self.assertEqual(
                count,num_slices,
                "There are more slices in OM than expected")
            count = Experiment.objects.filter(slice_id=i).count()
            self.assertEqual(count, 0, "Slice in OM has not deleted!")
            count = ExperimentFLowSpace.objects.filter(
                exp__slice_id = i).count() 
            self.assertEqual(
                count, 0,
                "FlowSpace associated with experiment slice_id" +\
                "=%d has not deleted completely" % i)            
    def test_optin(self):
        from expedient.common.tests.client import Browser
        from openflow.optin_manager.opts.models import UserOpts, OptsFlowSpace 
        from openflow.optin_manager.opts.models import AdminFlowSpace, UserFlowSpace,Experiment, ExperimentFLowSpace
        from django.contrib.auth.models import User
        #make a normal user on system
        username = "user"
        password = "password"
        u = User.objects.create(username=username, is_active=True)
        u.set_password(password)
        u.save()

        
        #assign a flowspace to the user and experiment
        self.user_ip_src_s = random.randint(0,0x80000000) & 0xFFFF0000
        self.user_ip_src_e = random.randint(0x80000000,0xFFFFFFFF) & 0xFFFF0000
      
        self.exp_ip_src_s = random.randint(0,0x80000000) & 0xFFFF0000
        self.exp_ip_src_e = random.randint(0x80000000,0xFFFFFFFF) & 0xFFFF0000
        fields=["dl_src","dl_dst","vlan_id","tp_src","tp_dst"]
        random.shuffle(fields)


        from openflow.optin_manager.xmlrpc_server.ch_api import om_ch_translate
        (to_str,from_str,width,om_name,of_name) = om_ch_translate.attr_funcs[fields[0]]
        self.user_field_name = om_name
        self.user_field_s = random.randint(0,2**width-3)
        self.user_field_e = self.user_field_s + 1
        (to_str,from_str,width,om_name,of_name) = om_ch_translate.attr_funcs[fields[1]]
        self.exp_field_name = om_name
        self.exp_field_s = random.randint(0,2**width-3)
        self.exp_field_e = self.exp_field_s + 1  
        
        # assign full flowspace to admin:
        adm = User.objects.get(username="admin")
        AdminFlowSpace.objects.create(user=adm)
        
        #assign flowspace to user
        ufs = UserFlowSpace(user=u, ip_src_s=self.user_ip_src_s,
                             ip_src_e=self.user_ip_src_e,approver=adm)
        setattr(ufs,"%s_s"%self.user_field_name,self.user_field_s)
        setattr(ufs,"%s_e"%self.user_field_name,self.user_field_e)
        ufs.save()     
        
        #create an experiment and assign a flowspace to it
        exp = Experiment.objects.create(slice_id="slice_id", project_name="project name",
                                  project_desc="project description", slice_name="slice name",
                                  slice_desc="slice description", controller_url="controller url",
                                  owner_email="owner email", owner_password="owner password") 
        expfs = ExperimentFLowSpace.objects.create(exp=exp, dpid="00:00:00:00:00:00:01",
                            ip_src_s=self.exp_ip_src_s, 
                            ip_src_e=self.exp_ip_src_e, 
                             )
        setattr(expfs,"%s_s"%self.exp_field_name,self.exp_field_s)
        setattr(expfs,"%s_e"%self.exp_field_name,self.exp_field_e)
        expfs.save() 
        
        # First authenticate
        b = Browser()

        logged_in = b.login(SCHEME+"://%s:%s/accounts/login/"%
                            (test_settings.HOST, test_settings.OM_PORT),
                            "user","password")
        self.assertTrue(logged_in,"Could not log in")
        
        g = b.get_and_post_form(SCHEME+"://%s:%s/opts/opt_in"%
                                (test_settings.HOST, test_settings.OM_PORT),
                                dict(experiment=1))
        
        uopt = UserOpts.objects.filter(user__username__exact="user")[0]
        
        self.assertEqual(uopt.priority , 1)
        
        optfs = OptsFlowSpace.objects.filter(opt = uopt)[0]
        self.assertEqual(optfs.ip_src_s , max(self.user_ip_src_s,self.exp_ip_src_s))
        self.assertEqual(optfs.ip_src_e , min(self.user_ip_src_e,self.exp_ip_src_e))
        self.assertEqual(getattr(optfs,"%s_s"%self.user_field_name), self.user_field_s)
        self.assertEqual(getattr(optfs,"%s_e"%self.user_field_name), self.user_field_e)
        self.assertEqual(getattr(optfs,"%s_s"%self.exp_field_name), self.exp_field_s)
        self.assertEqual(getattr(optfs,"%s_e"%self.exp_field_name), self.exp_field_e)

        # now test opt out:
        g = b.get_and_post_form(SCHEME+"://%s:%s/opts/opt_out"%
                                (test_settings.HOST, test_settings.OM_PORT),
                                {"1":"checked"})
        optfs = OptsFlowSpace.objects.filter(opt = uopt)
        self.assertEqual(optfs.count(),0) 
        self.create_more_exps()  
        
if __name__ == '__main__':
    import unittest
    unittest.main()
