'''
Created on Jun 7, 2010

@author: jnaous
'''

import logging
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from expedient.common.middleware import threadlocals
from ..models import ExpedientPermission, PermissionRequest, Permittee
from ..exceptions import PermissionDenied, PermissionCannotBeDelegated
from ..views import request_permission
from ..shortcuts import create_permission, give_permission_to
from views import other_perms_view, add_perms_view
from models import PermissionTestClass
from expedient.common.tests import manager as test_mgr
from expedient.common.permissions.models import ObjectPermission,\
    PermissionOwnership
from expedient.common.permissions.shortcuts import must_have_permission,\
    has_permission
from expedient.common.permissions.templatetags.permissions import has_obj_perm,\
    as_class

def _request_perm_wrapper(*args, **kwargs):
    return request_permission(
        reverse("test_allowed"),
        template="permissions/empty.html")(*args, **kwargs)

def create_objects(test_case):
    # Create test objects
    test_case.objs = []
    for _ in xrange(2):
        test_case.objs.append(PermissionTestClass.objects.create(val=1))
        
    # Create 3 users (1 superuser)
    test_case.su = User.objects.create_superuser(
        "superuser", "su@su.com", "password")
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
        create_permission(perm, view=other_perms_view)
    create_permission("can_get_x2")
    create_permission("can_add", view=add_perms_view)
    create_permission("test_request_perm", view=_request_perm_wrapper)
    
    # Give permissions to users
    for obj in test_case.objs:
        for perm in ["can_read_val", "can_get_x2", "can_get_x5"]:
            give_permission_to(perm,
                               obj,
                               test_case.u1,
                               can_delegate=True)
        for perm in ["can_read_val", "can_get_x3"]:
            give_permission_to(perm,
                               obj,
                               test_case.u2,
                               can_delegate=False)
        for perm in ["can_get_x4"]:
            give_permission_to(perm,
                               obj,
                               test_case.o3,
                               can_delegate=True)

        give_permission_to("test_request_perm",
                           PermissionTestClass,
                           test_case.u1,
                           can_delegate=True)

class TestObjectPermissions(test_mgr.SettingsTestCase):
    def setUp(self):
        from django.conf import settings
        self.settings_manager.set(
            INSTALLED_APPS=settings.INSTALLED_APPS + [
                'expedient.common.permissions.tests',
            ],
        )
        self.settings_manager.set(DEBUG_PROPAGATE_EXCEPTIONS=True)
        self.logger = logging.getLogger("TestObjectPermissions")
        create_objects(self)
        
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
        
        self.assertTrue(target == self.objs[1] and\
                        missing == ExpedientPermission.objects.get(
                            name="can_get_x2"))
        
        missing, target = ExpedientPermission.objects.get_missing(
            self.su, ["can_get_x2", "can_read_val"],
            PermissionTestClass.objects.all())
        
        self.assertTrue(target == None)
        self.assertTrue(missing == None)
        
    def test_get_missing_for_target(self):
        """
        Tests that the get_missing_for_target method of
        L{models.ExpedientPermissionManager} is correct.
        """
        
        missing = ExpedientPermission.objects.get_missing_for_target(
            self.u1, ["can_get_x2", "can_get_x3"], self.objs[0])
        
        self.assertTrue(
            missing == ExpedientPermission.objects.get(name="can_get_x3"))
        
        missing = ExpedientPermission.objects.get_missing_for_target(
            self.u1, ["can_get_x2", "can_read_val"], self.objs[0])
        
        self.assertTrue(missing == None)

        missing = ExpedientPermission.objects.get_missing_for_target(
            self.o3, ["can_get_x2", "can_read_val"], self.o3)

        self.assertTrue(missing == None)

        missing = ExpedientPermission.objects.get_missing_for_target(
            self.o3, ["can_get_x2", "can_read_val"], self.objs[1])
        
        self.assertTrue(
            missing == ExpedientPermission.objects.get(name="can_get_x2"))

        missing = ExpedientPermission.objects.get_missing_for_target(
            self.su, ["can_get_x2", "can_read_val"],
            self.objs[0])
        
        self.assertTrue(missing == None)
        
    def test_must_have_permission(self):
        """
        Tests the must_have_permission shortcut.
        """
        self.assertRaises(
            PermissionDenied,
            must_have_permission,
            permittee=self.u1,
            target_obj_or_class=self.objs[0],
            perm_name="can_get_x3",
        )

    def test_get_missing_permittee_same_as_target(self):
        """
        Tests that a permittee always has all permissions on itself.
        """
        missing = ExpedientPermission.objects.get_missing(
            self.u1, ["can_get_x2", "can_read_val"],
            User.objects.filter(id__in=[self.u1.id]))
        self.assertTrue(missing == (None, None))        

        give_permission_to("can_get_x2", self.u2, self.u1)
        give_permission_to("can_read_val", self.u2, self.u1)
        missing = ExpedientPermission.objects.get_missing(
            self.u1, ["can_get_x2", "can_read_val"],
            User.objects.filter(id__in=[self.u1.id, self.u2.id]))
        self.assertTrue(missing == (None, None))       

        missing = ExpedientPermission.objects.get_missing(
            self.o3, ["can_get_x2", "can_read_val"],
            PermissionTestClass.objects.filter(id__in=[self.o3.id]))
        self.assertTrue(missing == (None, None))    
        
    def test_filter_for_obj_permission(self):
        """
        Tests that the filter_for_obj_permission returns a list of all users
        who own the permission.
        """
        obj_permission =\
            ObjectPermission.objects.get_or_create_for_object_or_class(
                "can_read_val", self.o3)[0]
        
        permittees = Permittee.objects.filter_for_obj_permission(
            obj_permission, can_delegate=False)
        self.assertEqual(
            set(permittees),
            set([Permittee.objects.get_as_permittee(obj) \
                 for obj in [self.su, self.u1, self.u2]])
        )

        permittees = Permittee.objects.filter_for_obj_permission(
            obj_permission, can_delegate=True)
        self.assertEqual(
            set(permittees),
            set([Permittee.objects.get_as_permittee(obj) \
                 for obj in [self.su, self.u1]])
        )

    def test_obj_method_decorators(self):
        """
        Tests that the L{require_obj_permissions} and
        L{require_obj_permissions_for_user} are correct.
        """
        threadlocals.push_frame()
        d = threadlocals.get_thread_locals()
        
        for obj in self.objs:
            d["user_kw"] = self.u1
            self.assertEqual(obj.get_val_x2(), 2)
            d["user_kw"] = self.u2
            self.assertEqual(obj.get_val_x3_other_val(), 3)
            d["test_kw"] = self.o3
            self.assertEqual(obj.get_val_x4(), 4)
            d["user_kw"] = self.u1
            self.assertEqual(obj.get_val_x5_username(), 5)
        
        for obj in self.objs:
            d["user_kw"] = self.u2
            self.assertRaises(PermissionDenied, obj.get_val_x2, obj)
            d["user_kw"] = self.o3
            if obj != self.o3:
                self.assertRaises(PermissionDenied, obj.get_val_x3_other_val)
            d["test_kw"] = self.objs[1]
            if obj != self.objs[1]:
                self.assertRaises(PermissionDenied, obj.get_val_x4)
            d["user_kw"] = self.u2
            self.assertRaises(PermissionDenied, obj.get_val_x5_username, obj)

    def test_delegation(self):
        """
        Tests that permission delegation works correctly.
        """
        threadlocals.push_frame()
        d = threadlocals.get_thread_locals()
        d["user_kw"] = self.u2
        d["test_kw"] = self.u1

        # Test allowed delegation
        self.assertRaises(PermissionDenied, self.objs[0].get_val_x2,
                          self.objs[0])
        self.assertRaises(PermissionDenied, self.objs[1].get_val_x2,
                          self.objs[1])
        
        give_permission_to("can_get_x2", self.objs[0], self.u2,
                           giver=self.u1, can_delegate=True)
        
        self.assertEqual(self.objs[0].get_val_x2(), 2)
        self.assertRaises(PermissionDenied, self.objs[1].get_val_x2,
                          self.objs[1])

        give_permission_to("can_get_x2", self.objs[1], self.u2,
                           giver=self.u1, can_delegate=False)

        self.assertEqual(self.objs[1].get_val_x2(), 2)
        
        # Test disallowed delegation
        self.assertRaises(PermissionCannotBeDelegated,
                          give_permission_to,
                          "can_get_x3", self.objs[0], self.u1,
                          giver=self.u2, can_delegate=False)
        
        d["user_kw"] = self.u1
        self.assertRaises(PermissionDenied, self.objs[0].get_val_x3_other_val,
                          self.objs[0])
        self.assertRaises(PermissionDenied, self.objs[1].get_val_x3_other_val,
                          self.objs[1])
        
        # Test cross delegation between types
        give_permission_to("can_get_x4", self.objs[0], self.u1,
                           giver=self.o3, can_delegate=False)
        
        self.assertEqual(self.objs[0].get_val_x4(), 4)

        # Test delegation of delegated permission
        self.assertRaises(PermissionCannotBeDelegated,
                          give_permission_to,
                          "can_get_x4", self.objs[0], self.u2,
                          giver=self.u1, can_delegate=False)
        
        give_permission_to("can_get_x2", self.objs[0], self.o3,
                           giver=self.u2, can_delegate=True)

    def test_has_obj_perm(self):
        """Tests that the C{has_obj_perm} template filter works."""
        
        permittees = has_obj_perm(self.o3, "can_read_val")
        self.assertEqual(
            set(permittees),
            set([Permittee.objects.get_as_permittee(obj) \
                 for obj in [self.su, self.u1, self.u2]])
        )
        
    def test_as_class(self):
        """Tests that the C{as_class} template filter works"""
        
        permittees = \
            as_class(has_obj_perm(self.o3, "can_read_val"), User)
            
        self.assertEqual(
            set(permittees),
            set([self.su, self.u1, self.u2])
        )
        
    def test_delete_all_for_target(self):
        permittee = Permittee.objects.get_as_permittee(self.u1)
        
        # get the permissions the permittee has
        perms_count = ObjectPermission.objects.filter_from_instance(
            self.objs[0]).filter(permittees=permittee).count()
            
        self.assertTrue(perms_count > 0)
        
        # now call delete all for target
        PermissionOwnership.objects.delete_all_for_target(
            self.objs[0], self.u1)
        
        # check they are all gone
        perms_count = ObjectPermission.objects.filter_from_instance(
            self.objs[0]).filter(permittees=permittee).count()
        self.assertEqual(perms_count, 0)
        
    def test_get_permitted_objects(self):
        permitted = ObjectPermission.objects.get_permitted_objects(
            klass=PermissionTestClass,
            perm_names=["can_read_val"],
            permittee=self.u1
        )
        
        self.assertEqual(permitted.count(), 2)
        
        for obj in self.objs:
            self.assertTrue(obj in permitted)

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
        self.logger = logging.getLogger("TestRequests")
        create_objects(self)
        
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

        self.assertRaises(
            PermissionDenied,
            self.client.get,
            reverse("test_view_x2",
                    kwargs={"obj_id": self.objs[0].id}),
            follow=True)
        
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
                permittee_ct_id=ContentType.objects.get_for_model(User).id,
                permittee_id = self.u1.id,
                target_ct_id=ContentType.objects.get_for_model(ContentType).id,
                target_id=ContentType.objects.get_for_model(PermissionTestClass).id,
            )
        )
        self.assertRedirects(response, add_perm_url)
        self.assertEqual(self.client.session['from_url'],
                         reverse("test_view_crud"))
        
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
                permittee_ct_id=ContentType.objects.get_for_model(User).id,
                permittee_id = self.u1.id,
                target_ct_id=ContentType.objects.get_for_model(ContentType).id,
                target_id=ContentType.objects.get_for_model(PermissionTestClass).id,
            )
        )
        self.client.session['from_url'] = reverse("test_view_crud")
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
                permittee_ct_id=ContentType.objects.get_for_model(User).id,
                permittee_id = self.u1.id,
                target_ct_id=ContentType.objects.get_for_model(PermissionTestClass).id,
                target_id=self.objs[0].id,
            )
        )
        
        # try to update: Disallowed
        response = self.client.post(
            view_url,
            {"val": 5})
        self.assertRedirects(response, other_perm_url)
        self.assertEqual(self.client.session['from_url'], view_url)
        
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
                permittee_ct_id=ContentType.objects.get_for_model(User).id,
                permittee_id = self.u1.id,
                target_ct_id=ContentType.objects.get_for_model(ContentType).id,
                target_id=ContentType.objects.get_for_model(PermissionTestClass).id,
            )
        )
        self.assertRedirects(response, perm_url)
        self.assertEqual(
            self.client.session['from_url'], reverse("test_protected_url"))
        
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
                permittee_ct_id=ContentType.objects.get_for_model(User).id,
                permittee_id = self.u2.id,
                target_ct_id=ContentType.objects.get_for_model(ContentType).id,
                target_id=ContentType.objects.get_for_model(PermissionTestClass).id,
            )
        )
        self.assertRedirects(response, perm_url)
        self.assertEqual(
            self.client.session['from_url'], reverse("test_request_perm"))
        
        # post a request for the permission
        self.assertEqual(PermissionRequest.objects.count(), 0)
        response = self.client.post(perm_url, {"permission_owner": self.u1.id,
                                               "message": "hello",})
        self.assertRedirects(response, reverse("test_allowed"))
        self.assertEqual(PermissionRequest.objects.count(), 1)
        perm_req = PermissionRequest.objects.all()[0]
        self.assertEqual(perm_req.requesting_user, self.u2)
        self.assertEqual(
            perm_req.permittee,
            Permittee.objects.get_as_permittee(self.u2))
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
        
