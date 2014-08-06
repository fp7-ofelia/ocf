'''
Created on Oct 6, 2010

@author: jnaous
'''
from django.conf import settings
from expedient.common.tests.manager import SettingsTestCase
from django.contrib.auth.models import User
from expedient.common.middleware import threadlocals
from openflow.dummyom.models import DummyOM
from expedient.common.tests.client import test_get_and_post_form
from django.core.urlresolvers import reverse
from expedient.clearinghouse.geni.gopenflow.tests.models import DummyOFAggregate
from openflow.plugin.models import OpenFlowAggregate, OpenFlowSwitch,\
    OpenFlowInterface, OpenFlowInterfaceSliver, FlowSpaceRule,\
    OpenFlowSliceInfo
from expedient.common.rpc4django import views as rpc4django_views

from rpc import *
from openflow.plugin.gapi.rspec import parse_external_rspec, create_resv_rspec
from expedient.common.utils import create_or_update
from expedient.clearinghouse.users.models import UserProfile
from expedient.clearinghouse.project.models import Project
import random
from expedient.clearinghouse.geni.gopenflow.models import GCFOpenFlowAggregate
from expedient.clearinghouse.geni.models import GENISliceInfo

MOD = "geni.gopenflow"

class Tests(SettingsTestCase):
    urls = MOD + ".tests.urls"
    
    def setUp(self):
        """
        Update settings, create DummyOMs and test models and login.
        """
        # add the test application
        self.settings_manager.set(
            INSTALLED_APPS=settings.INSTALLED_APPS + [MOD + ".tests"],
            DEBUG_PROPAGATE_EXCEPTIONS=True,
        )
        
        logger.debug("Updating RPC dispatchers.")
        
        rpc4django_views._register_rpcmethods(
            [MOD + ".tests"],
            restrict_introspection=False,
            dispatchers=rpc4django_views.dispatchers)
        
        self.su = User.objects.create_superuser(
            "superuser", "bla@bla.com", "password")
        self.client.login(username="superuser", password="password")

        om = DummyOM.objects.create()
        om.populate_links(5, 10)

        # Add the aggregate to the CH
        test_get_and_post_form(
            self.client, reverse("openflow_aggregate_create"),
            dict(
                name="DummyOM",
                description="DummyOM Description",
                location="Stanford, CA",
                usage_agreement="Do you agree?",
                username="superuser",
                password="password",
                url="test://testserver:80/dummyom/1/xmlrpc/",
            )
        )
        
        self.of = DummyOFAggregate.objects.create()
        
        # now get the list of resources and store it, then delete the
        # OpenFlowAggregate.
        self.of.snapshot_switches()
        OpenFlowAggregate.objects.all().delete()
        
        # set defaults for SSL_CLIENT_CERT and REMOTE_USER
        tl = threadlocals.get_thread_locals()
        #tl["test_client_transport_defaults"]["REMOTE_USER"] = 
        
    def sort_switches(self, switches):
        for s in switches:
            for k in switches.keys():
                switches[k] = set(switches[k])
        return switches
        
    def links_to_set(self, links):
        return set([l[:-1] for l in links])
        
    def test_add_aggregate(self):
        resp = test_get_and_post_form(
            self.client, reverse("gopenflow_aggregate_create"),
            dict(
                name="DummyOF",
                description="DummyOF Description",
                location="Stanford, CA",
                url="test://testserver:80"+reverse("dummy_gopenflow"),
            )
        )
        self.assertEqual(GCFOpenFlowAggregate.objects.count(), 1)
        self.assertRedirects(
            resp,
            expected_url=reverse(
                "gopenflow_aggregate_add_links",
                args=[GCFOpenFlowAggregate.objects.all()[0].id]),
        )
        exp_switches, exp_links = parse_external_rspec(self.of.adv_rspec)
        
        new_rspec = gapi.ListResources({}, None)
        new_switches, new_links = parse_external_rspec(new_rspec)
        self.assertEqual(
            self.sort_switches(new_switches),
            self.sort_switches(exp_switches))
        self.assertEqual(
            self.links_to_set(new_links),
            self.links_to_set(exp_links))
        
    def test_reserve_sliver(self):
        
        self.test_add_aggregate()
        
        proj_name = "test project"
        proj_desc = "test project description"
        slice_name = "test slice"
        slice_desc = "test slice description"
        username = "test_user"
        firstname = "gapi"
        lastname = "user"
        password = "password"
        affiliation = "Stanford"
        email = "gapi_user@expedient.stanford.edu"
        controller_url = "tcp:bla.com:6633"
        fs1 = dict(
            dl_dst=("11:22:33:44:55:66", None),
            dl_type=(1234, 1236),
            vlan_id=(4455, 4455),
            nw_src=("123.123.132.123", "222.222.222.222"),
        )
        fs2 = dict(
            dl_src=("11:22:33:44:55:66", "11:22:33:44:55:77"),
            dl_dst=("11:22:33:44:55:66", None),
            dl_type=(1234, 1236),
            vlan_id=(None, 4455),
            nw_src=("123.123.132.123", "222.222.222.222"),
            nw_proto=(4,4),
            tp_src=(123,123),
        )
        
        agg = GCFOpenFlowAggregate.objects.all()[0]
        
        # setup threadlocals
        tl = threadlocals.get_thread_locals()
        tl["user"] = self.su
        
        project = Project.objects.create(
            name=proj_name, description=proj_desc,
        )
        tl["project"] = project

        url = reverse("project_add_agg", args=[project.id])
        response = self.client.post(
            path=url,
            data={"id": agg.id},
        )
        
        self.assertTrue(project.aggregates.count() == 1)
        
        self.assertRedirects(
            response,
            url,
        )
        
        slice = Slice.objects.create(
            project=project,
            name=slice_name,
            description=slice_desc,
            owner=self.su,
        )
        tl["slice"] = slice
        
        # To avoid expensive key creation
        info = GENISliceInfo.objects.get(slice=slice)
        info.ssh_private_key="abc"
        info.ssh_public_key = "def"
        info.save()
        
        slice_add_agg_url = reverse("slice_add_agg", args=[slice.id])

        # add aggregate to slice
        gopenflow_aggregate_slice_add_url = reverse(
            "gopenflow_aggregate_slice_add",
            kwargs={
                "agg_id": agg.id,
                "slice_id": slice.id,
            }
        )

        # post the form to add aggregate to slice
        response = self.client.post(
            path=slice_add_agg_url,
            data={"id": agg.id},
        )
        
        # should go the openflow special add aggregates page
        self.assertRedirects(
            response,
            gopenflow_aggregate_slice_add_url + "?next=" + slice_add_agg_url,
        )
    
        # Set the slice info
        response = test_get_and_post_form(
            self.client,
            gopenflow_aggregate_slice_add_url+ "?next=" + slice_add_agg_url,
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
            slice.aggregates.count(), 1,
            "Did not add aggregate to slice.")
        
        # select ports and switches
        random.seed(0)
        fs1_switches = random.sample(list(OpenFlowSwitch.objects.all()), 2)
        fs1_ports = random.sample(list(OpenFlowInterface.objects.all()), 2)
        fs2_switches = random.sample(list(OpenFlowSwitch.objects.all()), 2)
        fs2_ports = random.sample(list(OpenFlowInterface.objects.all()), 2)
        
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
        
        def add_switch_slivers(rule, switches):
            for s in switches:
                ports = OpenFlowInterface.objects.filter(switch=s)
                for p in ports:
                    sliver, _ = OpenFlowInterfaceSliver.objects.get_or_create(
                        slice=slice, resource=p)
                    rule.slivers.add(sliver)
        
        add_switch_slivers(r1, fs1_switches)
        add_switch_slivers(r2, fs2_switches)
    
        # get the expected reservation rspec
        exp_rspec = create_resv_rspec(self.su, slice)
        
        slice.start(self.su)
        actual_rspec = DummyOFAggregate.objects.all()[0].resv_rspec
        
        self.assertEqual(exp_rspec, actual_rspec)
        
    
