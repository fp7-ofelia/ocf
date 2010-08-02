'''
Created on Jul 29, 2010

@author: jnaous
'''
from django.test import TestCase
from django.contrib.auth.models import User
from expedient.common.permissions.shortcuts import create_permission,\
    give_permission_to, has_permission
from expedient.common.permissions.models import PermissionRequest,\
    Permittee, ObjectPermission
from django.core.urlresolvers import reverse
from expedient.common.tests.client import test_get_and_post_form

class RequestsTests(TestCase):
    def setUp(self):
        """
        Create some permissions and users.
        """
        self.u1 = User.objects.create_user("user1", "user@user.com", "password")
        self.u2 = User.objects.create_user("user2", "user@user.com", "password")
        
        create_permission("permission1", description="Permission 1 description.")
        give_permission_to("permission1", self.u1, self.u1, can_delegate=True)
        give_permission_to("permission1", self.u2, self.u1, can_delegate=True)
        
    def test_req_process(self):
        """
        Test that when a request is made for a user, it shows up in the
        dashboard.
        """
        self.client.login(username="user1", password="password")
        resp = self.client.get(reverse("permissionmgmt_dashboard"))
        
        # "permission1" should not be mentioned anywhere on the page
        self.assertContains(resp, "permission1", 0)
        
        obj_perm1=ObjectPermission.objects.get_or_create_for_object_or_class(
             "permission1", self.u1,
        )[0]
        obj_perm2=ObjectPermission.objects.get_or_create_for_object_or_class(
             "permission1", self.u2,
        )[0]
        req1 = PermissionRequest.objects.create(
            requesting_user=self.u2,
            permittee=Permittee.objects.get_or_create_from_instance(self.u2)[0],
            permission_owner=self.u1,
            requested_permission=obj_perm1,
        )
        req2 = PermissionRequest.objects.create(
            requesting_user=self.u2,
            permittee=Permittee.objects.get_or_create_from_instance(self.u2)[0],
            permission_owner=self.u1,
            requested_permission=obj_perm2,
        )
        
        resp = self.client.get(reverse("permissionmgmt_dashboard"))
        
        # "permission1" should be mentioned twice: once in each request
        self.assertContains(resp, "permission1", 2)
        
        resp = test_get_and_post_form(
            self.client, reverse("permissionmgmt_dashboard"),
            dict(
                approved=[str(req2.id)],
                denied=[str(req1.id)],
            )
        )
        
        self.assertRedirects(resp, reverse("permissionmgmt_confirm_req"))
        
        resp = test_get_and_post_form(
            self.client, reverse("permissionmgmt_confirm_req"),
            dict(
                post="yes",
            )
        )
        
        self.assertRedirects(resp, reverse("home"))
        
        self.assertEqual(PermissionRequest.objects.count(), 0)
        
        self.assertTrue(has_permission(self.u2, self.u2, "permission1"))
        self.assertFalse(has_permission(self.u2, self.u1, "permission1"))
        