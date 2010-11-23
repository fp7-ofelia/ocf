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
from expedient.clearinghouse.aggregate.tests.models import DummyAggregate
from expedient.clearinghouse.aggregate.utils import get_aggregate_classes

logger = logging.getLogger("ProjectTests")

def common_setup(self):
    # Add the Aggregate test application
    self.settings_manager.set(
        INSTALLED_APPS=settings.INSTALLED_APPS + \
        ["expedient.clearinghouse.aggregate.tests"],
        AGGREGATE_PLUGINS=settings.AGGREGATE_PLUGINS + \
            (("expedient.clearinghouse.aggregate.tests.models.DummyAggregate",
              "dummy_agg",
              "expedient.clearinghouse.aggregate.tests.urls"),
            ),
        DEBUG_PROPAGATE_EXCEPTIONS=True,
    )
    try:
        del get_aggregate_classes.l
    except AttributeError:
        pass
    
    """Create users and aggregates"""
    self.su = User.objects.create_superuser(
        "superuser", "su@su.com", "password")
    self.u1 = User.objects.create_user(
        "user1", "u@u.com", "password")
    self.u2 = User.objects.create_user(
        "user2", "u@u.com", "password")
    
    self.client.login(username="superuser", password="password")
    threadlocals.push_frame(user=self.su)
    
    self.agg1 = DummyAggregate.objects.create(
        name="Agg1",
    )
    self.agg2 = DummyAggregate.objects.create(
        name="Agg2",
    )
    
    self.client.logout()
    threadlocals.pop_frame()
    
class TestModels(SettingsTestCase):
    def setUp(self):
        common_setup(self)
        
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

    def test_list(self):
        """
        Create a few projects and check the get.
        """
        pass
#        l = []
#        members = User.objects.all()[0:2]
#        self.client.login(username="superuser", password="password")
#        threadlocals.push_frame(user=self.su)
#        for p in xrange(3):
#            
#        threadlocals.pop_frame()
#        self.client.logout()
#        
#        # check that the members see 3 projects    
#        for i, m in enumerate(members):
#            self.client.login(username=m.username, password="password")
#            response = self.client.get(reverse("project_list"))
#            self.assertContains(response, "project0", 1)
#            self.assertContains(response, "description0", 1)
#            self.assertContains(response, "project1", 1)
#            self.assertContains(response, "description1", 1)
#            d = pq(response.content)
#            self.assertEqual(len(d('tr')), 4) # including headers
#        
#        # check that a nonmember doesn't see any projects
#        self.client.login(username=m.username, password="password")
#        response = self.client.get(reverse("project_list"))
#        self.assertNotContains(response, "project0", 1)
#        self.assertNotContains(response, "description0", 1)
#        self.assertNotContains(response, "project1", 1)
#        self.assertNotContains(response, "description1", 1)
#        d = pq(response.content)
#        self.assertEqual(len(d('tr')), 1)
        
    