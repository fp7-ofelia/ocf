'''
Created on Jul 12, 2010

@author: jnaous
'''

from openflow.dummyom.models import DummyOM, DummyOMSlice, DummyOMSwitch,\
    DummyCallBackProxy
from django.contrib.auth.models import User
from openflow.plugin.models import OpenFlowAggregate, OpenFlowInterface,\
    OpenFlowInterfaceSliver, FlowSpaceRule, OpenFlowConnection,\
    NonOpenFlowConnection
from expedient.common.xmlrpc_serverproxy.models import PasswordXMLRPCServerProxy
import logging
from django.core.urlresolvers import reverse
from expedient.common.tests.client import test_get_and_post_form
from expedient.clearinghouse.project.models import Project
from expedient.clearinghouse.slice.models import Slice
from base64 import b64decode
import pickle
from django.conf import settings
from expedient.common.tests.manager import SettingsTestCase
from expedient.clearinghouse.resources.models import Resource
from expedient.clearinghouse.aggregate.models import Aggregate
from expedient.common.permissions.shortcuts import give_permission_to
from expedient.common.middleware import threadlocals

logger = logging.getLogger("OpenFlowPluginTests")

NUM_DUMMY_OMS = 3
NUM_SWITCHES_PER_AGG = 10
NUM_LINKS_PER_AGG = 30
NUM_TEST_RESOURCES = 10
SCHEME = "test"
HOST = "testserver"

MOD = "openflow.plugin"

class Tests(SettingsTestCase):
    
    def setUp(self):
        """
        Update settings, create DummyOMs and test models and login.
        """
        # add the test application
        self.settings_manager.set(
            OPENFLOW_OTHER_RESOURCES=(
                ("expedient.clearinghouse.resources", "Resource"),
            ),
            DEBUG_PROPAGATE_EXCEPTIONS=True,
        )
        
        self.test_user = User.objects.create_user(
            "user", "user@user.com", "password")
        give_permission_to("can_add_aggregate", Aggregate, self.test_user)
        
        for i in range(NUM_DUMMY_OMS):
            om = DummyOM.objects.create()
            om.populate_links(NUM_SWITCHES_PER_AGG, 
                              NUM_LINKS_PER_AGG/2)
            username = "clearinghouse%s" % i
            password = "clearinghouse"
            u = User.objects.create_user(username, "ch@ch.com", password)
    
            # Add the aggregate to the CH
            url = SCHEME + "://%s/dummyom/%s/xmlrpc/" % (HOST, om.id)
            
            proxy = PasswordXMLRPCServerProxy.objects.create(
                username=username, password=password,
                url=url, verify_certs=False,
            )
    
            # test availability
            if not proxy.is_available():
                raise Exception("Problem: Proxy not available")

            proxy.delete()
            
        self.client.login(username="user", password="password")
            
    def test_create_aggregates(self):
        """
        Test that we can create an OpenFlow Aggregate using the create view.
        """
        for i in range(NUM_DUMMY_OMS):
            response = test_get_and_post_form(
                self.client, reverse("openflow_aggregate_create"),
                dict(
                    name="DummyOM %s" % i,
                    description="DummyOM Description",
                    location="Stanford, CA",
                    usage_agreement="Do you agree?",
                    username="clearinghouse%s" % i,
                    password="clearinghouse",
                    url="test://testserver:80/dummyom/%s/xmlrpc/" % (i+1),
                ))
            
            logger.debug("Created aggregate %s" % (i+1))
            
            self.assertRedirects(
                response,
                expected_url=reverse("openflow_aggregate_add_links", args=[i+1]),
            )
            
    def test_static_of_links(self):
        """
        Tests that we can add/delete openflow-to-openflow static links.
        """
        
        self.test_create_aggregates()
        
        i = 0
        url = reverse("openflow_aggregate_add_links", args=[i+1])
        
        local_iface = OpenFlowInterface.objects.filter(aggregate__pk=i+1)[0]
        remote_iface = OpenFlowInterface.objects.filter(aggregate__pk=i+2)[0]
        
        self.assertEqual(
            OpenFlowConnection.objects.filter(
                src_iface=local_iface, dst_iface=remote_iface).count(), 0)
        self.assertEqual(
            OpenFlowConnection.objects.filter(
                dst_iface=local_iface, src_iface=remote_iface).count(), 0)
        
        response = test_get_and_post_form(
            self.client, url,
            dict(
                remote_interface=remote_iface.pk,
                local_interface=local_iface.pk,
            ),
            del_params=["delete_links", "add_other_links"]
        )
        self.assertRedirects(
            response,
            expected_url=url,
        )
        
        to_link = OpenFlowConnection.objects.get(
            src_iface=local_iface, dst_iface=remote_iface)
        from_link = OpenFlowConnection.objects.get(
            dst_iface=local_iface, src_iface=remote_iface)
        
        # test delete
        response = test_get_and_post_form(
            self.client, url,
            dict(
                of_connections=[to_link.pk, from_link.pk],
            ),
            del_params=["add_links", "add_other_links"],
        )
        print response
        self.assertRedirects(
            response,
            expected_url=url,
        )
        
        self.assertEqual(
            OpenFlowConnection.objects.filter(
                src_iface=local_iface, dst_iface=remote_iface).count(), 0)
        self.assertEqual(
            OpenFlowConnection.objects.filter(
                dst_iface=local_iface, src_iface=remote_iface).count(), 0)

    def test_static_non_of_links(self):
        """
        Tests that we can add/delete openflow-to-openflow static links.
        """
        
        self.test_create_aggregates()
        
        i = 0
        url = reverse("openflow_aggregate_add_links", args=[i+1])
        
        iface = OpenFlowInterface.objects.filter(aggregate__pk=i+1)[0]

        threadlocals.push_frame(user=self.test_user)
        self.generic_agg = Aggregate.objects.create(
            name="TestAggregate", owner=self.test_user)
        
        self.non_of_rsc = []
        resource = Resource.objects.create(
            name="TestResource%s" % i,
            aggregate=self.generic_agg,
        )
        
        self.assertEqual(
            NonOpenFlowConnection.objects.filter(
                of_iface=iface, resource=resource).count(), 0)
        
        response = test_get_and_post_form(
            self.client, url,
            dict(
                of_iface=iface.pk,
                resource=resource.pk,
            ),
            del_params=["delete_links", "add_links"]
        )
        self.assertRedirects(
            response,
            expected_url=url,
        )
        
        cnxn = NonOpenFlowConnection.objects.get(
            of_iface=iface, resource=resource)
        
        # test delete
        response = test_get_and_post_form(
            self.client, url,
            dict(
                non_of_connections=[cnxn.pk],
            ),
            del_params=["add_links", "add_other_links"],
        )
        print response
        self.assertRedirects(
            response,
            expected_url=url,
        )
        
        self.assertEqual(
            NonOpenFlowConnection.objects.filter(
                of_iface=iface, resource=resource).count(), 0)

    def test_double_update(self):
        """
        Make sure updating twice works.
        """
        self.test_create_aggregates()
        OpenFlowAggregate.objects.all()[0].update_topology()
            
    def test_add_to_project(self):
        """
        Create a project, add first aggregate to project.
        """
        
        self.test_create_aggregates()
        
        # create project
        response = test_get_and_post_form(
            self.client,
            url=reverse("project_create"),
            params=dict(
                name="project",
                description="description",
            )
        )
        
        project = Project.objects.all()[0]

        self.assertRedirects(
            response,
            reverse("project_detail", args=[project.id]),
        )
        
        # add aggregates to project
        for i in range(1, 4):
            url = reverse("project_add_agg", args=[project.id])
            response = self.client.post(
                path=url,
                data={"%s" % i: "Select"},
            )
            
            self.assertTrue(project.aggregates.count() == i)
            
            self.assertRedirects(
                response,
                url,
            )
        
    def test_add_to_slice(self):
        """
        Add the aggregate to a slice.
        """
        self.test_add_to_project()
        
        # create slice
        response = test_get_and_post_form(
            self.client,
            url=reverse("slice_create", args=[1]),
            params=dict(
                name="slice",
                description="description",
            ),
        )
        
        slice = Slice.objects.all()[0]
        
        self.assertRedirects(
            response,
            reverse("slice_detail", args=[slice.id]),
        )
        
        slice_add_agg_url = reverse("slice_add_agg", args=[slice.id])
        # add aggregates to slice
        for i in range(1, 4):
            openflow_aggregate_slice_add_url = reverse(
                "openflow_aggregate_slice_add",
                kwargs={
                    "agg_id": i,
                    "slice_id": slice.id,
                }
            )

            # post the form to add aggregate to slice
            response = self.client.post(
                path=slice_add_agg_url,
                data={"%s" % i: "Select"},
            )
            
            # should go the openflow special add aggregates page
            self.assertRedirects(
                response,
                openflow_aggregate_slice_add_url+ "?next=" + slice_add_agg_url,
            )
        
            # Set the slice info
            response = test_get_and_post_form(
                self.client,
                openflow_aggregate_slice_add_url+ "?next=" + slice_add_agg_url,
                params=dict(
                    controller_url="tcp:blabla:6633",
                    password="password",
                )
            )
            
            self.assertRedirects(
                response,
                slice_add_agg_url,
            )
            
            self.assertEqual(
                slice.aggregates.count(), i,
                "Did not add aggregates to slice.")

    def test_start_slice(self):
        """
        Create a slice, add resources interfaces, add flowspace, start.
        """
        self.test_add_to_slice()
        
        slice = Slice.objects.all()[0]
        
        # Add all interfaces using slivers.
        for iface in OpenFlowInterface.objects.all():
            sliver = OpenFlowInterfaceSliver.objects.create(
                slice=slice, resource=iface)
            # Add FlowSpace
            FlowSpaceRule.objects.create(
                sliver=sliver,
                nw_src_start="0.0.0.0",
            )
            FlowSpaceRule.objects.create(
                sliver=sliver,
                nw_dst_start="0.0.0.0",
            )
        
        # start the slice.
        for agg in OpenFlowAggregate.objects.all():
            agg.start_slice(slice)
            
        # check that we get all the switches in the created slice
        for ds in DummyOMSlice.objects.all():
            dpids = ds.om.dummyomswitch_set.all().values_list("dpid", flat=True)
            slivers = pickle.loads(b64decode(ds.switch_slivers))
            self.assertEqual(len(dpids), len(slivers))

            # check that each dpid has two flowspaces for each port
            for s in slivers:
                dpid = s["datapath_id"]
                fs = s["flowspace"]
                self.assertTrue(dpid in dpids)
                self.assertEqual(
                    len(fs), 2*DummyOMSwitch.objects.get(dpid=dpid).nPorts)
            
