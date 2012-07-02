from expedient.common.tests.manager import SettingsTestCase
from expedient.common.tests.utils import wrap_xmlrpc_call
import xmlrpclib
from openflow.optin_manager.users.models import UserProfile
from django.contrib.auth.models import User
from expedient.common.utils.transport import TestClientTransport
from expedient.common.xmlrpc_serverproxy.models import BasicAuthServerProxy
from openflow.optin_manager.dummyfv.models import DummyFV,DummyFVDevice, DummyFVRule,\
         DummyFVSlice   
from openflow.optin_manager.xmlrpc_server.models import FVServerProxy
import logging
import random
from expedient.common.tests.client import Browser, test_get_and_post_form
from django.core.urlresolvers import reverse
from openflow.optin_manager.opts.models import Experiment,ExperimentFLowSpace, \
    UserFlowSpace, UserOpts, OptsFlowSpace, MatchStruct
from openflow.optin_manager.flowspace.utils import *

logger = logging.getLogger("OMXMLRPCTest")

TIMEOUT = 20
SCHEME = "test"
HOST = "testserver"
USE_RANDOM = False

class Tests(SettingsTestCase):
    
    def setUp(self):
        # Create the clearinghouse user
        username = "clearinghouse"
        password = "password"
        u = User.objects.create(username=username)
        u.set_password(password)
        u.save()
        
        profile = UserProfile.get_or_create_profile(u) 
        profile.is_clearinghouse_user = True
        profile.save()
        
        url = "http://%s:80/xmlrpc/xmlrpc/" % (
                HOST,
        )
        self.om_client = BasicAuthServerProxy(url,
                    username=username,
                    password=password,
                    transport=TestClientTransport())
        # Create dummy FV
        fv = DummyFV.objects.create()
        # Load up a fake topology in the Dummy FV
        fv.populateTopology(10, 20, use_random=USE_RANDOM)
            
        # create fake users for the Dummy FV
        username = "om"
        password = "password"
        u = User.objects.create(username=username)
        u.set_password(password)
        u.save()

        # Create the FV proxy connection
        FVServerProxy.objects.create(
            name="Flowvisor",
            username=username,
            password=password,

            url = SCHEME+"://%s:8443/dummyfv/1/xmlrpc/" % (
                    HOST,
            ),
        )
        
        self.test_admin = User.objects.create_superuser("admin", "admin@admin.com", "password")
    
    def test_ping(self):
        """
        Communications are up.
        """
        ret = wrap_xmlrpc_call(
            self.om_client.ping, ["PING"], {}, TIMEOUT)
        self.assertEqual(ret, "PONG: PING", "Ping returned %s." % ret)
    
        
    def test_get_switches(self):
        """
        Test that a slice can be created and the calls are routed to the
        FV correctly.
        """
        # TODO: Fix to also check the returned info
        self.dpids_info = wrap_xmlrpc_call(
            self.om_client.get_switches, [], {}, TIMEOUT)
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
            self.om_client.get_links, [], {}, TIMEOUT)
        links = set([tuple(l[:-1]) for l in links])


        # TODO add checking for the link_infos (link attributes)
        expected = set([(
            link.src_dev.dpid,
            link.src_port,
            link.dst_dev.dpid,
            link.dst_port) for link in DummyFVLink.objects.all()])

        
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
        Tests that the Clearinghouse password can be changed correctly.
        """
        from django.contrib.auth.models import User
        wrap_xmlrpc_call(
            self.om_client.change_password, ["new_password"], {},
            TIMEOUT)
        
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
            self.assertEqual(DummyFVRule.objects.filter(fv=fv).count(), 0)
          
          
    def test_update_slice(self):
        '''
        Test if updating a slice actually update that slice's information and not 
        re-create it
        '''
        self.test_create_slice(5)
        from openflow.tests.helpers import Flowspace
        from openflow.optin_manager.xmlrpc_server.ch_api import convert_star_int
        
        # get the switches into self.dpids_info
        self.test_get_switches()
        prev_len = ExperimentFLowSpace.objects.all().count()
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
            "slice_id": 5,
            "project_name": "project_name 2",
            "project_description": "project_description 2",
            "slice_name": "new slice name-5",
            "slice_description": "new slice_description",
            "controller_url": "bla:bla.bla.bla:6633",
            "owner_email": "bla@bla.com",
            "owner_password": "new password",
            "switch_slivers": switch_slivers,
        }

        # Create!
        ret = self.om_client.create_slice(
            args["slice_id"], args["project_name"], args["project_description"],
            args["slice_name"], args["slice_description"],
            args["controller_url"], args["owner_email"], args["owner_password"],
            args["switch_slivers"]
        )
        
        # now test that just one experiment exist and that is the 
        # updated version:
        
        # check the return value
        self.assertEqual(ret, {'error_msg': "", 'switches': []})
        
        # check the OM database to see if Experiment has been created correctly
        returned = Experiment.objects.filter(slice_id=args["slice_id"])

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
        new_len = expfs.count()
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
            self.assertEqual(DummyFVRule.objects.filter(fv=fv).count(), 0)
            
    def test_update_slice_and_optin(self):
        '''
        Test if updating a slice when there are some opt-ins actually update the opt-ins
        '''
        user_ip_addr_s = "192.168.0.123"
        user_ip_addr_e = "192.168.0.124"
        ip_addr_s = "192.168.0.123"
        ip_addr_e = "192.168.0.126"
        new_ip_addr_s = "192.168.0.125"
        new_ip_addr_e = "192.168.0.128"
        
        # create a user and assign a FS to him:
        u = User.objects.create_user("username", "user@user.com", "password")
        UserProfile.get_or_create_profile(u)
        UserFlowSpace.objects.create(user=u,approver=self.test_admin,
                                     ip_src_s=dotted_ip_to_int(user_ip_addr_s)
                                     ,ip_src_e=dotted_ip_to_int(user_ip_addr_e))
        args = {
            "slice_id": 1,
            "project_name": "project_name 1",
            "project_description": "project_description 1",
            "slice_name": "new slice name-1",
            "slice_description": "new slice_description",
            "controller_url": "bla:bla.bla.bla:6633",
            "owner_email": "bla@bla.com",
            "owner_password": "new password",
            "switch_slivers": [
                {
                "datapath_id": "00:00:00:00:00:00:01",
                "flowspace": [
                              {"nw_src_start":"%s"%ip_addr_s,"nw_src_send":"%s"%ip_addr_e},
                             ],
                },
                {
                "datapath_id": "00:00:00:00:00:00:02",
                "flowspace": [
                              {"nw_src_start":"%s"%new_ip_addr_s,"nw_src_send":"%s"%new_ip_addr_e},
                             ],
                },
            ]
        }
        
        # Create!
        ret = self.om_client.create_slice(
            args["slice_id"], args["project_name"], args["project_description"],
            args["slice_name"], args["slice_description"],
            args["controller_url"], args["owner_email"], args["owner_password"],
            args["switch_slivers"]
        )
        
        # now test that just one experiment exist and that is the 
        # updated version:
        
        # check the return value
        self.assertEqual(ret, {'error_msg': "", 'switches': []})
        
        # check the OM database to see if Experiment has been created correctly
        returned = Experiment.objects.filter(slice_id=args["slice_id"])

        self.assertEqual(
            returned.count(), 1 ,
            "more than one slice with same name %s" % args["slice_name"])
        
        # now opt-in user:
        self.client.login(username="username",password="password")
        response = test_get_and_post_form(
            self.client,
            reverse("opt_in_experiment"),
            {"experiment":1},
        )
        # now test if opt-in was correct
        self.assertContains(response, "successfully")
        optfs = OptsFlowSpace.objects.filter(opt__user=u)
        self.assertEqual(optfs.count(),1)
        
        self.assertEqual(optfs[0].dpid,"00:00:00:00:00:00:01")
        self.assertEqual(optfs[0].ip_src_s,dotted_ip_to_int(user_ip_addr_s))
        self.assertEqual(optfs[0].ip_src_e,dotted_ip_to_int(user_ip_addr_e))

        # now change the experiments flowspace, verify that user opt
        # updated accordingly:
        args = {
            "slice_id": 1,
            "project_name": "project_name 1",
            "project_description": "project_description 1",
            "slice_name": "new slice name-1",
            "slice_description": "new slice_description",
            "controller_url": "bla:bla.bla.bla:6633",
            "owner_email": "bla@bla.com",
            "owner_password": "new password",
            "switch_slivers": [
                {
                "datapath_id": "00:00:00:00:00:00:01",
                "flowspace": [
                              {"nw_src_start":"%s"%new_ip_addr_s,"nw_src_send":"%s"%new_ip_addr_e},
                             ],
                },
                {
                "datapath_id": "00:00:00:00:00:00:02",
                "flowspace": [
                              {"nw_src_start":"%s"%new_ip_addr_s,"nw_src_send":"%s"%new_ip_addr_e},
                             ],
                },
            ]
        }
        
        # Create!
        ret = self.om_client.create_slice(
            args["slice_id"], args["project_name"], args["project_description"],
            args["slice_name"], args["slice_description"],
            args["controller_url"], args["owner_email"], args["owner_password"],
            args["switch_slivers"]
        )
        
        # now test that just one experiment exist and that is the 
        # updated version:
        
        # check the return value
        self.assertEqual(ret, {'error_msg': "", 'switches': []})
        optfs = OptsFlowSpace.objects.filter(opt__user=u)
        self.assertEqual(optfs.count(),0)
                
            
    def test_delete_slice(self):
        """
        Tests that slices are deleted correctly from the OM to FV
        """

        num_slices = random.randint(1, 5)
        for i in range(num_slices):
            self.test_create_slice(id=i)
        
        # delete some slices and make sure they are gone
        ids = range(1, num_slices)
        random.shuffle(ids)
        for i in ids:
            err = wrap_xmlrpc_call(
                self.om_client.delete_slice, [i], {}, TIMEOUT)
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