'''
Created on Jun 11, 2010

@author: jnaous
'''

from expedient.common.tests.manager import SettingsTestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from models import Project
from pyquery import PyQuery as pq

import logging
logger = logging.getLogger("ProjectTests")

class Tests(SettingsTestCase):
    def setUp(self):
        # Add the user
        logger.debug("Creating users.")
        for i in xrange(2):
            u = User(username="user%s" % i)
            u.set_password("password")
            u.save()
        
        logger.debug("Setup done.")
        
    def test_list(self):
        """
        Create a few projects and check the get.
        """
        l = []
        members = User.objects.all()[0:2]
        for p in xrange(3):
            l.append(Project.objects.create(
                name="project"+p, description="description"+p,
                members=members, owner=members[0]))
        
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
