'''
Created on Jul 12, 2010

@author: jnaous
'''
from datetime import datetime, timedelta
import time        
from pyquery import PyQuery as pq
from lxml import etree as et
from openflow.dummyom.models import DummyOM, DummyOMSlice, DummyOMSwitch
from django.contrib.auth.models import User
from django.conf import settings
from openflow.plugin.models import OpenFlowAggregate, OpenFlowInterface,\
    OpenFlowInterfaceSliver, FlowSpaceRule, OpenFlowConnection,\
    NonOpenFlowConnection, OpenFlowSwitch, OpenFlowSliceInfo
from expedient.common.xmlrpc_serverproxy.models import PasswordXMLRPCServerProxy
import logging
from django.core.urlresolvers import reverse
from expedient.common.tests.client import test_get_and_post_form, parse_form
from expedient.clearinghouse.project.models import Project
from expedient.clearinghouse.slice.models import Slice
from base64 import b64decode
import pickle
from expedient.common.tests.manager import SettingsTestCase
from expedient.clearinghouse.resources.models import Resource
from expedient.clearinghouse.aggregate.models import Aggregate
from expedient.common.permissions.shortcuts import give_permission_to
from expedient.common.middleware import threadlocals
from openflow.plugin.gapi import rspec as rspec_mod
from expedient.clearinghouse.geni.utils import create_x509_cert, get_user_urn
from expedient.clearinghouse.geni import clearinghouse as geni_clearinghouse
from expedient.clearinghouse.users.models import UserProfile
import random
from expedient.common.federation.sfa.trust import credential
from expedient.clearinghouse.geni.models import GENISliceInfo
import xmlrpclib
from expedient.common.utils.transport import TestClientTransport
from expedient.common.utils import create_or_update
from expedient.common.federation.geni.util.urn_util import publicid_to_urn
from xmlrpclib import Fault

logger = logging.getLogger("OpenFlowPluginTests")

NUM_DUMMY_OMS = 3
NUM_SWITCHES_PER_AGG = 10
NUM_LINKS_PER_AGG = 30
NUM_TEST_RESOURCES = 10
SCHEME = "test"
HOST = "testserver"

MOD = "openflow.plugin"

logging.getLogger("OpenflowModelsParsing").setLevel(logging.WARNING)
logging.getLogger("TestClientTransport").setLevel(logging.WARNING)
logging.getLogger("rpc4django.views").setLevel(logging.WARNING)

def get_form_options(doc):
    """Return the values of all option tags"""
    d = pq(doc, parser="html")
    options = d("option")
    return [option.attrib["value"] for option in options]

def order_rspec(rspec):
    # order the flowspace and switch elements in the rspec
    root = et.fromstring(rspec)
    
    # sort the flowspace by its xml's length
    fs_elems = root.findall(".//flowspace")
    for elem in fs_elems:
        root.remove(elem)
    fs_elems = sorted(fs_elems, key=lambda fs:len(et.tostring(fs)))
    
    # then within each flowspace, sort the ports by their urn
    for fs_elem in fs_elems:
        port_elems = fs_elem.findall(".//port")
        for port_elem in port_elems:
            fs_elem.remove(port_elem)
        port_elems = sorted(port_elems, key=lambda port:port.get("urn"))
        for port_elem in port_elems:
            fs_elem.append(port_elem)
        root.append(fs_elem)
    
    return et.tostring(root)

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
        self.su = User.objects.create_superuser(
            "superuser", "bla@bla.com", "password")
        self.test_user_password = "password"
        self.test_user = User.objects.create_user(
            "test_user", "user@user.com", self.test_user_password)
        give_permission_to("can_add_aggregate", Aggregate, self.test_user)
        give_permission_to("can_create_project", Project, self.test_user)
        
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
            
        # create user cert/keys
        self.user_urn = get_user_urn(self.test_user.username)
        self.user_cert, self.user_key = create_x509_cert(self.user_urn)
        
        # get slice creds
        self.slice_cred = geni_clearinghouse.CreateSlice(
            self.user_cert.save_to_string())
        self.slice_gid = credential.Credential(
            string=self.slice_cred).get_gid_object()
        
        # xmlrpc client
        self.rpc = xmlrpclib.ServerProxy(
            "http://testserver" + reverse("openflow_gapi"),
            transport=TestClientTransport(
                defaults={
                    "REMOTE_USER": self.user_cert.save_to_string(),
                    "SSL_CLIENT_CERT": self.user_cert.save_to_string(),
                },
            ),
        )
        
    def test_create_aggregates(self):
        """
        Test that we can create an OpenFlow Aggregate using the create view.
        """
        self.client.login(
            username=self.test_user.username, password=self.test_user_password)
        
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
            
        self.assertEqual(OpenFlowAggregate.objects.count(), NUM_DUMMY_OMS)
            
    def test_static_of_links(self):
        """
        Tests that we can add/delete openflow-to-openflow static links.
        """
        
        self.test_create_aggregates()
        
        url = reverse("openflow_aggregate_add_links", args=[1])
        
        local_iface = OpenFlowInterface.objects.filter(aggregate__pk=1)[0]
        remote_iface = OpenFlowInterface.objects.filter(aggregate__pk=2)[0]
        
        disabled_iface = OpenFlowInterface.objects.filter(aggregate__pk=1)[1]
        disabled_iface.available = False
        disabled_iface.save()
        
        # check that there are no links already
        self.assertEqual(
            OpenFlowConnection.objects.filter(
                src_iface=local_iface, dst_iface=remote_iface).count(), 0)
        self.assertEqual(
            OpenFlowConnection.objects.filter(
                dst_iface=local_iface, src_iface=remote_iface).count(), 0)
        
        # check that disabled interfaces are not present and enabled ones are.
        response = self.client.get(url)
        opt_values = get_form_options(response.content)
        self.assertFalse(disabled_iface.id in opt_values)
        self.assertFalse(local_iface.id in opt_values)
        self.assertFalse(remote_iface.id in opt_values)
        
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
        
        # check that the new connection shows up
        response = self.client.get(url)
        d = pq(response.content, parser="html")
        cnxns = d("input[name='of_connections']")
        self.assertEqual(len(cnxns), 2)
        
        to_link = OpenFlowConnection.objects.get(
            src_iface=local_iface, dst_iface=remote_iface)
        from_link = OpenFlowConnection.objects.get(
            dst_iface=local_iface, src_iface=remote_iface)
        
        # disable an interface to see if the connection still shows
        local_iface.available = False
        local_iface.save()
        response = self.client.get(url)
        d = pq(response.content, parser="html")
        cnxns = d("input[name='of_connections']")
        self.assertEqual(len(cnxns), 0)
        
        # reenable the interface to see if the connection shows back up
        local_iface.available = True
        local_iface.save()
        response = self.client.get(url)
        d = pq(response.content, parser="html")
        cnxns = d("input[name='of_connections']")
        self.assertEqual(len(cnxns), 2)

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
            name="TestAggregate")
        
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

        # check that the new connection shows up
        response = self.client.get(url)
        d = pq(response.content, parser="html")
        cnxns = d("input[name='non_of_connections']")
        self.assertEqual(len(cnxns), 1)
        
        # disable an interface to see if the connection still shows
        iface.available = False
        iface.save()
        response = self.client.get(url)
        d = pq(response.content, parser="html")
        cnxns = d("input[name='non_of_connections']")
        self.assertEqual(len(cnxns), 0)
        
        # reenable the interface to see if the connection shows back up
        iface.available = True
        iface.save()
        response = self.client.get(url)
        d = pq(response.content, parser="html")
        cnxns = d("input[name='non_of_connections']")
        self.assertEqual(len(cnxns), 1)

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
                data={"id": i},
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
        
        expiration = datetime.now() \
            + timedelta(days=settings.MAX_SLICE_LIFE - 2)

        # create slice
        response = test_get_and_post_form(
            self.client,
            url=reverse("slice_create", args=[1]),
            params=dict(
                name="slice",
                description="description",
                expiration_date_0="%s" % expiration.date(),
                expiration_date_1=expiration.time().strftime("%H:%m:%S"),
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
                data={"id": i},
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
        
        # Add FlowSpace
        fs1 = FlowSpaceRule.objects.create(
            nw_src_start="0.0.0.0",
        )
        fs2 = FlowSpaceRule.objects.create(
            nw_dst_start="0.0.0.0",
        )
        # Add all interfaces using slivers.
        for iface in OpenFlowInterface.objects.all():
            sliver = OpenFlowInterfaceSliver.objects.create(
                slice=slice, resource=iface)
            fs1.slivers.add(sliver)
            fs2.slivers.add(sliver)
        
        # start the slice.
        self.client.post(reverse("slice_start", args=[slice.id]))

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
            
    def test_gapi_existing_slice(self):
        """Check that a slice created through the web or some other way is available through the gapi interface."""
        
        self.test_start_slice()
        
        slice = Slice.objects.all()[0]
        
        urn = GENISliceInfo.objects.all()[0].slice_urn
        rspec = self.rpc.ListResources(
            [self.slice_cred], {"geni_slice_urn": urn})
        
        # check that the returned rspec matches the created slice
        root = et.fromstring(rspec)
        ports = set([et.tostring(e) for e in root.findall(".//port")])
        num_ports = len(ports)
        
        num_slivers = OpenFlowInterfaceSliver.objects.filter(
            slice=slice).distinct().count()
        
        self.assertEqual(num_ports, num_slivers)
        
        flowspace = root.findall(".//flowspace")
        self.assertEqual(len(flowspace), 2)
    
    def test_gapi_GetVersion(self):
        self.assertEqual(self.rpc.GetVersion()["geni_api"], 1)
        
    def test_gapi_ListResources(self, create=True, zipped=False):
        # add aggregates
        if create:
            self.test_create_aggregates()
            self.client.logout()
        
        # get the rspec for the added resources
        options = dict(geni_compressed=zipped, geni_available=True)
        rspec = self.rpc.ListResources([self.slice_cred], options)
        
        logger.debug("Got advertisement RSpec:\n %s" % rspec)
        
        if zipped:
            import zlib, base64
            rspec = zlib.decompress(base64.b64decode(rspec))
            
        # parse the rspec and check the switches/links
        switches, links = rspec_mod.parse_external_rspec(rspec)
        
        # verify that all switches are listed
        dpids_actual = set(OpenFlowSwitch.objects.values_list(
            "datapath_id", flat=True))
        dpids_found = set(switches.keys())
        self.assertEqual(dpids_found, dpids_actual)
        
        # verify the ports for each switch
        for dpid in dpids_actual:
            ports_actual = set(OpenFlowInterface.objects.filter(
                switch__datapath_id=dpid).values_list(
                    "port_num", flat=True))
            ports_found = set(switches[dpid])
            self.assertEqual(ports_found, ports_actual)
            
        # verify the links
        links_actual = set(OpenFlowConnection.objects.values_list(
            "src_iface__switch__datapath_id", "src_iface__port_num",
            "dst_iface__switch__datapath_id", "dst_iface__port_num",
        ))
        links_found = set([l[:-1] for l in links])
        self.assertEquals(links_found, links_actual)
        
        
    def test_gapi_ZippedListResources(self):
        self.test_gapi_ListResources(zipped=True)
        
    def test_gapi_changed_ListResources(self):
        self.test_gapi_ListResources()
        for s in OpenFlowSwitch.objects.all()[:5]:
            s.delete()
        self.test_gapi_ListResources(create=False)
        
    def test_gapi_CreateSliver(self,
        proj_name = "test project",
        proj_desc = "test project description",
        slice_name = "test slice",
        slice_desc = "test slice description",
        username = "test_user",
        firstname = "gapi",
        lastname = "user",
        password = "password",
        affiliation = "Stanford",
        email = "gapi_user@expedient.stanford.edu",
        controller_url = "tcp:bla.com:6633",
        fs1 = dict(
            dl_dst=("11:22:33:44:55:66", None),
            dl_type=(1234, 1236),
            vlan_id=(4455, 4455),
            nw_src=("123.123.132.123", "222.222.222.222"),
        ),
        fs2 = dict(
            dl_src=("11:22:33:44:55:66", "11:22:33:44:55:77"),
            dl_dst=("11:22:33:44:55:66", None),
            dl_type=(1234, 1236),
            vlan_id=(None, 4455),
            nw_src=("123.123.132.123", "222.222.222.222"),
            nw_proto=(4,4),
            tp_src=(123,123),
        ),
        slice=None,
        expiration=datetime.now() + timedelta(days=1),
        create_aggregates=True,
    ):
        # IMPORTANT: If you change fs1 and fs2, make sure that
        # the rspec for fs1 is shorter than that for fs2 since
        # the test needs to order them by length.
        
        # add the aggregates
        if create_aggregates:
            self.test_create_aggregates()
            self.client.logout()
    
        # setup threadlocals
        tl = threadlocals.get_thread_locals()
        tl["user"] = self.su
        
        # create the info
        user, _ = create_or_update(
            model=User,
            filter_attrs={"username": username},
            new_attrs={
                "first_name": firstname,
                "last_name": lastname,
                "email": email,
            }
        )
        create_or_update(UserProfile,
            filter_attrs={
                "user": user,
            },
            new_attrs={
                "affiliation":affiliation,
            }
        )
        
        if slice:
            project = slice.project
            project.name = proj_name
            project.description = proj_desc
            project.save()
        else:
            project, _ = create_or_update(Project,
                filter_attrs=dict(name=proj_name),
                new_attrs=dict(description=proj_desc),
            )

        if not slice:
            slice = Slice.objects.create(
                project=project,
                name=slice_name,
                description=slice_desc,
                owner=user,
                expiration_date=expiration,
            )
        
        # select ports and switches
        random.seed(0)
        fs1_switches = random.sample(list(OpenFlowSwitch.objects.all()), 10)
        fs1_ports = random.sample(list(OpenFlowInterface.objects.all()), 10)
        fs2_switches = random.sample(list(OpenFlowSwitch.objects.all()), 10)
        fs2_ports = random.sample(list(OpenFlowInterface.objects.all()), 10)
        
        if slice:
            OpenFlowInterfaceSliver.objects.filter(
                slice=slice).delete()
            FlowSpaceRule.objects.filter(slivers__slice=slice).delete()
        
        def create_port_slivers(fs, ports):
            slivers = []
            for p in ports:
                slivers.append(OpenFlowInterfaceSliver.objects.create(
                    slice=slice, resource=p))
                kw = {}
                for k, r in fs.items():
                    if r[0]:
                        kw[k+"_start"] = r[0]
                    if r[1]:
                        kw[k+"_end"] = r[1]
                    
            rule = FlowSpaceRule.objects.create(**kw)
            for s in slivers:
                rule.slivers.add(s)
                
            return rule
        
        # create the slivers for the slice
        r1 = create_port_slivers(fs1, fs1_ports)
        r2 = create_port_slivers(fs2, fs2_ports)
        
        create_or_update(OpenFlowSliceInfo,
            filter_attrs=dict(slice=slice),
            new_attrs=dict(password=password, controller_url=controller_url),
        )
        
        # get the rspec using only the ports
        resv_rspec = rspec_mod.create_resv_rspec(user, slice)
        
        # add the full switches to the reservation rspec
        root = et.fromstring(resv_rspec)
        fs_elems = root.findall(".//%s" % rspec_mod.FLOWSPACE_TAG)
        
        def add_switches(elem, switches):
            for s in switches:
                et.SubElement(
                    elem, rspec_mod.SWITCH_TAG, {
                        rspec_mod.URN: rspec_mod._dpid_to_urn(s.datapath_id),
                    },
                )
                
        add_switches(fs_elems[0], fs1_switches)
        add_switches(fs_elems[1], fs2_switches)
        
        resv_rspec = et.tostring(root)
        
        # Now add the switches into the slice and get the expected rspec
        # that will be returned
        def add_switch_slivers(rule, switches):
            for s in switches:
                ports = OpenFlowInterface.objects.filter(switch=s)
                for p in ports:
                    sliver, _ = OpenFlowInterfaceSliver.objects.get_or_create(
                        slice=slice, resource=p)
                    rule.slivers.add(sliver)
        
        add_switch_slivers(r1, fs1_switches)
        add_switch_slivers(r2, fs2_switches)
        
        expected_resv_rspec = rspec_mod.create_resv_rspec(user, slice)
        
        # delete created state
        project.delete()
        user.delete()
        r1.delete()
        r2.delete()
        
        # create the slice using gapi
        ret_rspec = self.rpc.CreateSliver(
            self.slice_gid.get_urn(),
            [self.slice_cred],
            resv_rspec,
            {},
        )
        
        ret = order_rspec(ret_rspec)
        exp = order_rspec(expected_resv_rspec)
            
        self.assertEqual(
            ret,
            exp,
            "Expected:\n%s \nFound:\n%s" % (exp, ret),
        )
        
        # check that the created state is what is expected
        self.assertEqual(
            GENISliceInfo.objects.all()[0].slice_urn, self.slice_gid.get_urn())
        
        project = Project.objects.all()[0]
        self.assertEqual(project.name, proj_name)
        self.assertEqual(project.description, proj_desc)
        
        slice = Slice.objects.all()[0]
        self.assertEqual(slice.name, slice_name)
        self.assertEqual(slice.description, slice_desc)
        self.assertEqual(slice.project, project)
        self.assertEqual(
            long(time.mktime(slice.expiration_date.timetuple())),
            long(time.mktime(expiration.timetuple())),
        )
        
        user = User.objects.get(username=username)
        self.assertEqual(user.first_name, firstname)
        self.assertEqual(user.last_name, lastname)
        self.assertEqual(user.email, email)
        
        user_profile= UserProfile.objects.all()[0]
        self.assertEqual(user_profile.affiliation, affiliation)
        self.assertEqual(user, user)
        
        r1 = FlowSpaceRule.objects.all()[0]
        r2 = FlowSpaceRule.objects.all()[1]
        
        def verif_rule(r, fs):
            for field in "dl_src", "dl_dst", "dl_type", \
            "vlan_id", "nw_src", "nw_dst", "nw_proto", \
            "tp_src", "tp_dst":
                if field in fs:
                    self.assertEqual(fs[field][0], getattr(r, field+"_start"))
                    self.assertEqual(fs[field][1], getattr(r, field+"_end"))
                else:
                    self.assertEqual(None, getattr(r, field+"_start"))
                    self.assertEqual(None, getattr(r, field+"_end"))
        
        verif_rule(r1, fs1)
        verif_rule(r2, fs2)
        
        # check the slivers in rules: make sure each rule has all the
        # the interfaces it is supposed to have.
        def verif_slivers(r, ports, switches):
            all_ports = []
            all_ports.extend(ports)
            
            for s in switches:
                all_ports.extend(OpenFlowInterface.objects.filter(switch=s))
                
            all_ports = set(all_ports)
            
            # check number of interfaces
            self.assertEqual(len(all_ports), r.slivers.count())
            
            # check slivers
            for sliver in r.slivers.all():
                self.assertTrue(sliver.resource.as_leaf_class() in all_ports)
                
        verif_slivers(r1, fs1_ports, fs1_switches)
        verif_slivers(r2, fs2_ports, fs2_switches)
        
        return ret_rspec
        
    def test_gapi_expired_CreateSliver(self):
        try:
            self.test_gapi_CreateSliver(
                expiration=datetime.now() - timedelta(days=1),
            )
        except Fault:
            pass
        else:
            self.fail("Did not raise a Fault for expired slice.")
            
    def test_gapi_RenewSliver(self):
        self.test_gapi_CreateSliver()
        
        d = datetime.now() + timedelta(days=10)

        ret_rspec = self.rpc.RenewSliver(
            self.slice_gid.get_urn(),
            [self.slice_cred],
            d.strftime("%Y-%m-%dT%H:%M:%S"),
        )
        
        slice = Slice.objects.all()[0]
        
        self.assertEqual(
            long(time.mktime(slice.expiration_date.timetuple())),
            long(time.mktime(d.timetuple())),
        )
        
    def test_gapi_DeleteSliver(self):
        self.test_gapi_CreateSliver()
        self.rpc.DeleteSliver(self.slice_gid.get_urn(), [self.slice_cred])
        self.assertEqual(Slice.objects.count(), 0)
        self.assertEqual(GENISliceInfo.objects.count(), 0)
        self.assertEqual(Project.objects.count(), 0)
        self.assertEqual(OpenFlowInterfaceSliver.objects.count(), 0)
        self.assertEqual(FlowSpaceRule.objects.count(), 0)
        
    def test_gapi_slice_ListResources(self):
        expected_rspec = self.test_gapi_CreateSliver()
        ret_rspec = self.rpc.ListResources(
            [self.slice_cred], {"geni_slice_urn": self.slice_gid.get_urn()})
        self.assertEqual(ret_rspec, expected_rspec)
        
    def test_gapi_duplicate_slice_name(self):
        """Check that a slice with different urn but same name raises DuplicateSliceNameException."""
        
        resv_rspec = self.test_gapi_CreateSliver()
        
        # get new credentials with new urn
        self.slice_cred = geni_clearinghouse.CreateSlice(
            self.user_cert.save_to_string())
        self.slice_gid = credential.Credential(
            string=self.slice_cred).get_gid_object()
        
        # same slice different urn with same project name
        try:
            self.rpc.CreateSliver(
                self.slice_gid.get_urn(),
                [self.slice_cred],
                resv_rspec,
                {},
            )
        except xmlrpclib.Fault as e:
            self.assertEqual(e.faultCode, "Duplicate slice name.")
        else:
            self.fail("Did not generate expected fault.")
    
        # same slice different urn with different project name
        root = et.fromstring(resv_rspec)
        
        # change the project name
        elem = root.find(".//project")
        elem.set("name", "new proj name")
        resv_rspec = et.tostring(root)

        try:
            self.rpc.CreateSliver(
                self.slice_gid.get_urn(),
                [self.slice_cred],
                resv_rspec,
                {},
            )
        except xmlrpclib.Fault as e:
            self.assertEqual(e.faultCode, "Duplicate slice name.")
        else:
            self.fail("Did not generate expected fault.")

    def test_gapi_project_name_change_CreateSliver(self):
        resv_rspec = self.test_gapi_CreateSliver()
        new_proj_name = "new project name"
        root = et.fromstring(resv_rspec)
        
        # change the project name
        elem = root.find(".//project")
        elem.set("name", new_proj_name)
        resv_rspec = et.tostring(root)
        
        ret_rspec = self.rpc.CreateSliver(
            self.slice_gid.get_urn(),
            [self.slice_cred],
            resv_rspec,
            {},
        )

        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(Slice.objects.count(), 1)
        self.assertEqual(Project.objects.all()[0].name, new_proj_name)
        
        exp = order_rspec(resv_rspec)
        ret = order_rspec(ret_rspec)

        self.assertEqual(
            ret,
            exp,
            "Expected:\n%s \nFound:\n%s" % (exp, ret),
        )
        
    def test_gapi_slice_name_change_CreateSliver(self):
        resv_rspec = self.test_gapi_CreateSliver()
        new_slice_name = "new slice name"
        root = et.fromstring(resv_rspec)
        
        # change the project name
        elem = root.find(".//slice")
        elem.set("name", new_slice_name)
        resv_rspec = et.tostring(root)
        
        ret_rspec = self.rpc.CreateSliver(
            self.slice_gid.get_urn(),
            [self.slice_cred],
            resv_rspec,
            {},
        )

        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(Slice.objects.count(), 1)
        self.assertEqual(Slice.objects.all()[0].name, new_slice_name)
        
        exp = order_rspec(resv_rspec)
        ret = order_rspec(ret_rspec)

        self.assertEqual(
            ret,
            exp,
            "Expected:\n%s \nFound:\n%s" % (exp, ret),
        )
        
    def test_gapi_html_ui(self):
        """Test that we can see details of a slice created through the
         gapi interface in the HTML UI plugin."""
        
        rspec = self.test_gapi_CreateSliver()
        slice = Slice.objects.all()[0]
        
        # get the number of expected ports
        root = et.fromstring(rspec)
        ports = set([et.tostring(e) for e in root.findall(".//port")])
        num_ports = len(ports)
        
        # check the select resources page
        self.client.login(
            username=self.su, password="password")
        resp = self.client.get(reverse("slice_detail", args=[slice.id]))

        self.assertEqual(resp.status_code, 200)
        d = pq(resp.content, parser="html")
        checked = d(":checked")
        
        self.assertEqual(
            OpenFlowSwitch.objects.count(),
            NUM_SWITCHES_PER_AGG*NUM_DUMMY_OMS)
        self.assertEqual(num_ports, OpenFlowInterfaceSliver.objects.count())
        self.assertEqual(len(checked), num_ports)
        
        # check the select flowspace page
        resp = self.client.get(
            reverse("flowspace", args=[slice.id]))
        self.assertEqual(resp.status_code, 200)
        d = pq(resp.content, parser="html")
        tables = d("table.saved")
        self.assertEqual(2, len(tables))
        
    def test_external_rspec(self):
        self.test_create_aggregates()
        adv_rspec = rspec_mod.get_resources(None, None)
        
        d1 = rspec_mod.parse_external_rspec(adv_rspec)
        
        # replace all the urn prefixes with external ones
        test_prefix = publicid_to_urn(
            "IDN %s//%s" % ("test//test", settings.OPENFLOW_GCF_BASE_SUFFIX)
        )
        adv_rspec2 = adv_rspec.replace(
            rspec_mod.OPENFLOW_GAPI_RSC_URN_PREFIX, test_prefix)

        d2 = rspec_mod.parse_external_rspec(adv_rspec2)
        
        self.assertEqual(d1, d2)

