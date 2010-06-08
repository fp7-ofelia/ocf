'''
Created on Jun 7, 2010

@author: jnaous
'''

from django.test import TestCase
from expedient.common.permissions.models import PermissionTestClass,\
    ExpedientPermission
from django.contrib.auth.models import User
from expedient.common.permissions.utils import register_permission,\
    give_permission_to
from expedient.common.permissions.exceptions import PermissionDenied,\
    PermissionCannotBeDelegated

import logging

def logging_set_up(level):
    if not hasattr(logging, "setup_done"):
        if level == logging.DEBUG:
            format = '%(asctime)s:%(name)s:%(levelname)s:%(pathname)s:%(lineno)s:%(message)s'
        else:
            format = '%(asctime)s:%(name)s:%(levelname)s:%(message)s'
        logging.basicConfig(level=level, format=format)
    logging.setup_done = True

class TestObjectPermissions(TestCase):
    def setUp(self):
        logging_set_up(logging.DEBUG)
        self.logger = logging.getLogger("TestObjectPermissions")
        # Create test objects
        self.objs = []
        for i in xrange(2):
            self.objs.append(PermissionTestClass.objects.create(val=1))
            
        # Create 2 users
        self.u1 = User.objects.create(username="test1")
        self.u2 = User.objects.create(username="test2")
        self.o3 = self.objs[0]
        
        # create permissions
        for perm in ["can_read_val", "can_get_x2", "can_get_x3",
                     "can_get_x4", "can_get_x5"]:
            register_permission(perm)
            
        # Give permissions to users
        for obj in self.objs:
            for perm in ["can_read_val", "can_get_x2", "can_get_x5"]:
                give_permission_to(self.u1,
                                   perm,
                                   obj,
                                   delegatable=True)
            for perm in ["can_read_val", "can_get_x3"]:
                give_permission_to(self.u2,
                                   perm,
                                   obj,
                                   delegatable=False)
            for perm in ["can_get_x4"]:
                give_permission_to(self.o3,
                                   perm,
                                   obj,
                                   delegatable=True)
                
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

