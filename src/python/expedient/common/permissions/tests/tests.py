'''
Created on Jun 7, 2010

@author: jnaous
'''

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from ..models import ExpedientPermission, PermissionRequest
from ..utils import create_permission, give_permission_to
from ..exceptions import PermissionDenied, PermissionCannotBeDelegated
from ..views import request_permission
from views import other_perms_view, add_perms_view
from models import PermissionTestClass
from expedient.common.tests import manager as test_mgr

import logging

LOGGING_LEVEL = logging.DEBUG

def logging_set_up(level):
    if not hasattr(logging, "setup_done"):
        if level == logging.DEBUG:
            format = '%(asctime)s:%(name)s:%(levelname)s:%(pathname)s:%(lineno)s:%(message)s'
        else:
            format = '%(asctime)s:%(name)s:%(levelname)s:%(message)s'
        logging.basicConfig(level=level, format=format)
    logging.setup_done = True

def _request_perm_wrapper(*args, **kwargs):
    return request_permission(
        reverse("test_allowed"),
        template="permissions/empty.html")(*args, **kwargs)

def create_objects(test_case):
        # Create test objects
        test_case.objs = []
        for i in xrange(2):
            test_case.objs.append(PermissionTestClass.objects.create(val=1))
            
        # Create 2 users
        test_case.u1 = User.objects.create(username="test1")
        test_case.u1.set_password("password")
        test_case.u1.save()
        test_case.u2 = User.objects.create(username="test2")
        test_case.u2.set_password("password")
        test_case.u2.save()
        test_case.o3 = test_case.objs[0]
        
        # create permissions
        for perm in ["can_read_val", "can_get_x3", "can_call_protected_url",
                     "can_get_x4", "can_get_x5", "can_set_val"]:
            create_permission(perm, other_perms_view)
        create_permission("can_get_x2")
        create_permission("can_add", add_perms_view)
        create_permission("test_request_perm", _request_perm_wrapper)
        
        # Give permissions to users
        for obj in test_case.objs:
            for perm in ["can_read_val", "can_get_x2", "can_get_x5"]:
                give_permission_to(test_case.u1,
                                   perm,
                                   obj,
                                   delegatable=True)
            for perm in ["can_read_val", "can_get_x3"]:
                give_permission_to(test_case.u2,
                                   perm,
                                   obj,
                                   delegatable=False)
            for perm in ["can_get_x4"]:
                give_permission_to(test_case.o3,
                                   perm,
                                   obj,
                                   delegatable=True)

            give_permission_to(test_case.u1, "test_request_perm",
                               PermissionTestClass,
                               delegatable=True)

class TestObjectPermissions(test_mgr.SettingsTestCase):
    def setUp(self):
        self.settings_manager.set(INSTALLED_APPS=(
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'expedient.common.permissions',
            'expedient.common.permissions.tests',
        ))
        self.settings_manager.set(DEBUG_PROPAGATE_EXCEPTIONS=True)
        logging_set_up(LOGGING_LEVEL)
        self.logger = logging.getLogger("TestObjectPermissions")
        create_objects(self)
        self.logger.debug("Done setup")
        
    def test_get_missing(self):
        """
        Tests that the get_missing method of L{models.ExpedientPermissionManager}
        is correct.
        """
        missing, target = ExpedientPermission.objects.get_missing(
            self.u1, ["can_get_x2", "can_get_x3"],
            PermissionTestClass.objects.all())
        
        self.assertTrue(target == self.objs[0])
        self.assertTrue(
            missing == ExpedientPermission.objects.get(name="can_get_x3"))
        
        missing, target = ExpedientPermission.objects.get_missing(
            self.u1, ["can_get_x2", "can_read_val"],
            PermissionTestClass.objects.all())
        
        self.assertTrue(target == None and missing == None)

        missing, target = ExpedientPermission.objects.get_missing(
            self.o3, ["can_get_x2", "can_read_val"],
            PermissionTestClass.objects.all())
        
        self.logger.debug("missing: %s, target: %s" % (missing, target))
        self.assertTrue(target == self.objs[0] and\
                        missing == ExpedientPermission.objects.get(
                            name="can_get_x2"))
        
    def test_get_missing_for_target(self):
        """
        Tests that the get_missing_for_target method of
        L{models.ExpedientPermissionManager} is correct.
        """
        
        missing, target = ExpedientPermission.objects.get_missing_for_target(
            self.u1, ["can_get_x2", "can_get_x3"], self.objs[0])
        
        self.assertTrue(target == self.objs[0])
        self.assertTrue(
            missing == ExpedientPermission.objects.get(name="can_get_x3"))
        
        missing, target = ExpedientPermission.objects.get_missing_for_target(
            self.u1, ["can_get_x2", "can_read_val"], self.objs[0])
        
        self.assertTrue(target == None and missing == None)

        missing, target = ExpedientPermission.objects.get_missing_for_target(
            self.o3, ["can_get_x2", "can_read_val"], self.objs[0])
        
        self.assertTrue(target == self.objs[0] and\
                        missing == ExpedientPermission.objects.get(name="can_get_x2"))

    def test_obj_method_decorators(self):
        """
        Tests that the L{require_obj_permissions} and
        L{require_obj_permissions_for_user} are correct.
        """
        
        for obj in self.objs:
            self.assertEqual(obj.get_val_x2(user_kw=self.u1), 2)
            self.assertEqual(obj.get_val_x3_other_val(user_kw=self.u2), (3, self.u2))
            self.assertEqual(obj.get_val_x4(test_kw=self.o3), 4)
            self.assertEqual(obj.get_val_x5_username(user=self.u1), (5, self.u1.username))
        
        for obj in self.objs:
            self.assertRaises(PermissionDenied, obj.get_val_x2, obj, user_kw=self.u2)
            self.assertRaises(PermissionDenied, obj.get_val_x3_other_val, obj, user_kw=self.o3)
            self.assertRaises(PermissionDenied, obj.get_val_x4, obj, test_kw=self.objs[1])
            self.assertRaises(PermissionDenied, obj.get_val_x5_username, obj, user=self.u2)

    def test_delegation(self):
        """
        Tests that permission delegation works correctly.
        """
        
        # Test allowed delegation
        self.assertRaises(PermissionDenied, self.objs[0].get_val_x2,
                          self.objs[0], user_kw=self.u2)
        self.assertRaises(PermissionDenied, self.objs[1].get_val_x2,
                          self.objs[1], user_kw=self.u2)
        
        give_permission_to(self.u2, "can_get_x2", self.objs[0],
                           giver=self.u1, delegatable=True)
        
        self.assertEqual(self.objs[0].get_val_x2(user_kw=self.u2), 2)
        self.assertRaises(PermissionDenied, self.objs[1].get_val_x2,
                          self.objs[1], user_kw=self.u2)

        give_permission_to(self.u2, "can_get_x2", self.objs[1],
                           giver=self.u1, delegatable=False)

        self.assertEqual(self.objs[1].get_val_x2(user_kw=self.u2), 2)
        
        # Test disallowed delegation
        self.assertRaises(PermissionCannotBeDelegated,
                          give_permission_to,
                          self.u1, "can_get_x3", self.objs[0],
                          giver=self.u2, delegatable=False)
        
        self.assertRaises(PermissionDenied, self.objs[0].get_val_x3_other_val,
                          self.objs[0], user_kw=self.u1)
        self.assertRaises(PermissionDenied, self.objs[1].get_val_x3_other_val,
                          self.objs[1], user_kw=self.u1)
        
        # Test cross delegation between types
        give_permission_to(self.u1, "can_get_x4", self.objs[0],
                           giver=self.o3, delegatable=False)
        
        self.assertEqual(self.objs[0].get_val_x4(test_kw=self.u1), 4)

        # Test delegation of delegated permission
        self.assertRaises(PermissionCannotBeDelegated,
                          give_permission_to,
                          self.u2, "can_get_x4", self.objs[0],
                          giver=self.u1, delegatable=False)
        
        give_permission_to(self.o3, "can_get_x2", self.objs[0],
                           giver=self.u2, delegatable=True)

class TestRequests(test_mgr.SettingsTestCase):
    urls = 'expedient.common.permissions.tests.test_urls'
    
    def setUp(self):
        self.settings_manager.set(INSTALLED_APPS=(
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'expedient.common.permissions',
            'expedient.common.permissions.tests',
        ))
        self.settings_manager.set(DEBUG_PROPAGATE_EXCEPTIONS=True)
        logging_set_up(LOGGING_LEVEL)
        self.logger = logging.getLogger("TestRequests")
        create_objects(self)
        self.logger.debug("Done setup")
        
    def test_allowed_request(self):
        """
        Tests that an allowed get works for a protected view.
        """
        self.client.login(username="test1", password="password")

        # Get the view
        response = self.client.get(reverse("test_view_x2",
                                           kwargs={"obj_id": self.objs[0].id}))
        self.assertContains(response, "2", 1, 200)

        response = self.client.post(reverse("test_view_x2",
                                            kwargs={"obj_id": self.objs[0].id}))
        self.assertContains(response, "2", 1, 200)
        
    def test_disallowed_request_no_redirect(self):
        """
        Tests that a permission with no view defined just raises an error.
        """
        self.client.login(username="test2", password="password")

        self.assertRaises(PermissionDenied,
                          self.client.get,
                          reverse("test_view_x2",
                                  kwargs={"obj_id": self.objs[0].id}))
        
    def test_disallowed_redirect(self):
        """
        Tests that the "can_add" permission is applied correctly for the
        L{PermissionTestClass} and that we are redirected to obtain the
        permission
        """
        self.client.login(username="test1", password="password")

        # Get the view
        response = self.client.get(reverse("test_view_crud"))
        self.assertEqual(response.status_code, 200)
        
        # Test create not allowed
        response = self.client.post(reverse("test_view_crud"), {"val": 3})
        add_perm_url = reverse(
            "permissions_url",
            kwargs=dict(
                perm_name="can_add",
                user_ct_id=ContentType.objects.get_for_model(User).id,
                user_id = self.u1.id,
                target_ct_id=ContentType.objects.get_for_model(ContentType).id,
                target_id=ContentType.objects.get_for_model(PermissionTestClass).id,
            )
        ) + "?next=/tests/test_view_crud/"
        self.assertRedirects(response, add_perm_url)
        
        f = PermissionTestClass.objects.all().count()
        self.assertEqual(f, 2,
            "Created object: expected count %s found %s." % (2, f))
        
    def test_get_permission(self):
        """
        Get the permission to create then create.
        """
        self.client.login(username="test1", password="password")
        
        # Get permission
        add_perm_url = reverse(
            "permissions_url",
            kwargs=dict(
                perm_name="can_add",
                user_ct_id=ContentType.objects.get_for_model(User).id,
                user_id = self.u1.id,
                target_ct_id=ContentType.objects.get_for_model(ContentType).id,
                target_id=ContentType.objects.get_for_model(PermissionTestClass).id,
            )
        ) + "?next=/tests/test_view_crud/"
        response = self.client.post(add_perm_url)
        self.assertRedirects(response, reverse("test_view_crud"))
        
        response = self.client.post(reverse("test_view_crud"), {"val": 3})
        self.assertRedirects(response, reverse("test_view_crud"))
        
        f = PermissionTestClass.objects.all().count()
        self.assertEqual(f, 3,
            "Did not create object: expected count %s found %s." % (3, f))
        
    def test_protected_post(self):
        """
        Try to post to a view protected by an object permission. Should redirect
        to get permission. Get permission, then try to post again.
        """
        
        self.client.login(username="test1", password="password")
        
        # Get permission url
        view_url = reverse("test_view_update", kwargs={"obj_id": self.objs[0].id})
        other_perm_url = reverse(
            "permissions_url",
            kwargs=dict(
                perm_name="can_set_val",
                user_ct_id=ContentType.objects.get_for_model(User).id,
                user_id = self.u1.id,
                target_ct_id=ContentType.objects.get_for_model(PermissionTestClass).id,
                target_id=self.objs[0].id,
            )
        ) + "?next=%s" % view_url
        
        # try to update: Disallowed
        response = self.client.post(
            view_url,
            {"val": 5})
        self.assertRedirects(response, other_perm_url)
        
        # get permission
        response = self.client.post(other_perm_url)
        self.assertRedirects(response, view_url)
        
        # Try to update: Allowed
        response = self.client.post(
            view_url,
            {"val": 5})
        self.assertRedirects(response, view_url)
        
        obj = PermissionTestClass.objects.get(id=self.objs[0].id)
        self.assertEqual(obj.val, 5)
        
    def test_protected_url(self):
        """
        Try to access a protected url.
        """
        
        self.client.login(username="test1", password="password")
        
        # Test create not allowed
        response = self.client.post(reverse("test_protected_url"))
        perm_url = reverse(
            "permissions_url",
            kwargs=dict(
                perm_name="can_call_protected_url",
                user_ct_id=ContentType.objects.get_for_model(User).id,
                user_id = self.u1.id,
                target_ct_id=ContentType.objects.get_for_model(ContentType).id,
                target_id=ContentType.objects.get_for_model(PermissionTestClass).id,
            )
        ) + "?next=%s" % reverse("test_protected_url")
        self.assertRedirects(response, perm_url)
        
    def test_request_permission(self):
        """
        Test the generic request_permission view for permissions.
        """
        self.client.login(username="test2", password="password")

        # get should be disallowed
        response = self.client.get(reverse("test_request_perm"))
        perm_url = reverse(
            "permissions_url",
            kwargs=dict(
                perm_name="test_request_perm",
                user_ct_id=ContentType.objects.get_for_model(User).id,
                user_id = self.u2.id,
                target_ct_id=ContentType.objects.get_for_model(ContentType).id,
                target_id=ContentType.objects.get_for_model(PermissionTestClass).id,
            )
        ) + "?next=%s" % reverse("test_request_perm")
        self.assertRedirects(response, perm_url)
        
        # post a request for the permission
        self.assertEqual(PermissionRequest.objects.count(), 0)
        response = self.client.post(perm_url, {"permission_owner": 1,
                                               "message": "hello",})
        self.assertRedirects(response, reverse("test_allowed"))
        self.assertEqual(PermissionRequest.objects.count(), 1)
        perm_req = PermissionRequest.objects.all()[0]
        self.assertEqual(perm_req.requesting_user, self.u2)
        self.assertEqual(perm_req.permission_owner, self.u1)
        self.assertEqual(
            perm_req.requested_permission.target,
            ContentType.objects.get_for_model(PermissionTestClass))
        self.assertEqual(perm_req.requested_permission.permission.name,
                         "test_request_perm")
        self.assertEqual(perm_req.message, "hello")
        
        perm_req.allow()

        # get should be allowed now
        response = self.client.get(reverse("test_request_perm"))
        self.assertEqual(response.status_code, 200)
        
