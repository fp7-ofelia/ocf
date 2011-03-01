'''
Created on Jun 11, 2010

@author: jnaous
'''

import logging
from expedient.common.tests.manager import SettingsTestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from models import Project
from pyquery import PyQuery as pq
from expedient.common.middleware import threadlocals
from expedient.common.permissions.shortcuts import give_permission_to,\
    has_permission
from django.conf import settings
from expedient.clearinghouse.aggregate.tests.models import DummyAggregate,\
    DummyResource, DummySliceEvent
from expedient.clearinghouse.aggregate.utils import get_aggregate_classes
from expedient.common.tests.client import test_get_and_post_form
from expedient.clearinghouse.slice.models import Slice
from expedient.clearinghouse.resources.models import Sliver
from expedient.clearinghouse.roles.models import ProjectRole
from expedient.clearinghouse.utils import add_dummy_agg_to_test_settings,\
    start_test_slice

logger = logging.getLogger("ProjectTests")

def common_setup(self):
    # Add the Aggregate test application
    add_dummy_agg_to_test_settings(self)
    
class TestModels(SettingsTestCase):
    def setUp(self):
        common_setup(self)
        
        self.su = User.objects.create_superuser(
            "superuser", "su@su.com", "password")
        
        self.client.login(username="superuser", password="password")
        threadlocals.push_frame(user=self.su)
        
        self.agg1 = DummyAggregate.objects.create(
            name="Agg1",
        )
        self.agg1.create_resources()
        
        self.agg2 = DummyAggregate.objects.create(
            name="Agg2",
        )
        self.agg2.create_resources()
        
        self.client.logout()
        threadlocals.pop_frame()
            
    def test_allowed_create(self, name="test"):
        """Tests that we can create a project"""

        self.client.login(username="superuser", password="password")
        threadlocals.push_frame(user=self.su)
        p = Project.objects.create(
            name=name,
            description="description",
        )
        threadlocals.pop_frame()
        self.client.logout()
        return p
        
    def test_get_permittees(self):
        p1 = self.test_allowed_create()
        self.test_allowed_create(name="test2")
        permittees = p1.members_as_permittees
        self.assertEqual(
            permittees.count(), 1,
            "Got permittees %s instead of just %s" % (permittees, self.su)
        )
        
    def test_get_aggregates(self):
        proj = self.test_allowed_create()
        
        self.assertEqual(proj.aggregates.count(), 0)
        
        give_permission_to("can_use_aggregate", self.agg1, proj)
        self.assertTrue(has_permission(proj, self.agg1, "can_use_aggregate"))
        self.assertEqual(proj.aggregates.count(), 1)
        self.assertTrue(self.agg1.aggregate_ptr in proj.aggregates)
        
class TestRequests(SettingsTestCase):
    def setUp(self):
        common_setup(self)
        
    def test_full(self):
        """
        Test that a project with a started slice can be deleted.
        """
        
        start_test_slice(self)
        
        slice_name = "%s" % self.slice
        
        self.client.login(
            username=self.u2.username, password="password")
        threadlocals.push_frame(user=self.u2)

        # delete the project. This should delete all the slivers
        # and resources, and delete the slice. It should also stop
        # the slice (which creates a DummySliceEvent)
        response = test_get_and_post_form(
            client=self.client,
            url=self.project.get_delete_url(),
            params={},
        )
        self.assertRedirects(response, "/")

        self.assertEqual(
            DummySliceEvent.objects.filter(
                slice=slice_name, status="stopped").count(), 2)
        self.assertEqual(Sliver.objects.count(), 0)
        self.assertEqual(Project.objects.count(), 0)
        
        self.client.logout()
        threadlocals.pop_frame()
        
        
