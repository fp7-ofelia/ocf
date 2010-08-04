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
from expedient.clearinghouse.aggregate.models import Aggregate

logger = logging.getLogger("ProjectTests")

class TestModels(SettingsTestCase):
    def setUp(self):
        """Create users and aggregates"""
        self.su = User.objects.create_superuser(
            "superuser", "su@su.com", "password")
        self.u1 = User.objects.create_user(
            "user1", "u@u.com", "password")
        self.u2 = User.objects.create_user(
            "user2", "u@u.com", "password")
        
        self.client.login(username="superuser", password="password")
        threadlocals.push_frame(user=self.su)
        
        self.agg1 = Aggregate.objects.create(
            name="Agg1",
        )
        self.agg2 = Aggregate.objects.create(
            name="Agg2",
        )
        
        self.client.logout()
        threadlocals.pop_frame()
        
    def test_allowed_create(self):
        """Tests that we can create a project"""

        self.client.login(username="superuser", password="password")
        threadlocals.push_frame(user=self.su)
        
        
    def test_list(self):
        """
        Create a few projects and check the get.
        """
        l = []
        members = User.objects.all()[0:2]
        for p in xrange(3):
            l.append(Project.objects.create(
                name="project%s" % p, description="description%s" % p))
        
        # check that the members see 3 projects    
        for i, m in enumerate(members):
            self.client.login(username=m.username, password="password")
            response = self.client.get(reverse("project_list"))
            self.assertContains(response, "project0", 1)
            self.assertContains(response, "description0", 1)
            self.assertContains(response, "project1", 1)
            self.assertContains(response, "description1", 1)
            d = pq(response.content)
            self.assertEqual(len(d('tr')), 4) # including headers
        
        # check that a nonmember doesn't see any projects
        self.client.login(username=m.username, password="password")
        response = self.client.get(reverse("project_list"))
        self.assertNotContains(response, "project0", 1)
        self.assertNotContains(response, "description0", 1)
        self.assertNotContains(response, "project1", 1)
        self.assertNotContains(response, "description1", 1)
        d = pq(response.content)
        self.assertEqual(len(d('tr')), 1)
