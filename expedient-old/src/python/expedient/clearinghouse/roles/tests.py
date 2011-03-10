'''
Created on Aug 3, 2010

@author: jnaous
'''
from django.test import TestCase
from django.contrib.auth.models import User
from expedient.clearinghouse.project.models import Project
from expedient.common.middleware import threadlocals
from expedient.clearinghouse.roles.models import ProjectRole
from expedient.common.permissions.shortcuts import create_permission,\
    has_permission
from expedient.common.permissions.models import ObjectPermission,\
    PermissionOwnership
from expedient.common.permissions.exceptions import PermissionCannotBeDelegated
from expedient.clearinghouse.roles.utils import get_users_for_role

class TestModels(TestCase):
    def setUp(self):
        """Create a project and test permissions and permittees"""
        self.su = User.objects.create_superuser(
            "superuser", "su@su.com", "password")
        self.u1 = User.objects.create_user(
            "user1", "u@u.com", "password")
        self.u2 = User.objects.create_user(
            "user2", "u@u.com", "password")
        self.u3 = User.objects.create_user(
            "user3", "u@u.com", "password")
        
        
        self.client.login(username="superuser", password="password")
        threadlocals.push_frame(user=self.su)

        self.project = Project.objects.create(
            name="projectX", description="blabla")
        self.projectY = Project.objects.create(
            name="projectY", description="blabla")
        
        self.client.logout()
        threadlocals.pop_frame()
        
        create_permission("perm1")
        create_permission("perm2")
        create_permission("perm3")
        create_permission("perm4")
        
        self.obj_perm1 = ObjectPermission.objects.\
            get_or_create_for_object_or_class("perm1", self.project)[0]
        self.obj_perm2 = ObjectPermission.objects.\
            get_or_create_for_object_or_class("perm2", self.project)[0]
        self.obj_perm3 = ObjectPermission.objects.\
            get_or_create_for_object_or_class("perm3", self.project)[0]
        self.obj_perm4 = ObjectPermission.objects.\
            get_or_create_for_object_or_class("perm4", self.project)[0]
        
        self.role1 = ProjectRole.objects.create(
            name="role1", project=self.project,
        )
        self.role1.obj_permissions.add(self.obj_perm1)
        
        self.role2 = ProjectRole.objects.create(
            name="role2", project=self.project,
        )
        self.role2.obj_permissions.add(self.obj_perm2)

        self.role3 = ProjectRole.objects.create(
            name="role3", project=self.project,
        )
        self.role3.obj_permissions.add(self.obj_perm1)
        self.role3.obj_permissions.add(self.obj_perm3)
        
        create_permission("permY1")
        create_permission("permY2")
        create_permission("permY3")
        create_permission("permY4")
        
        self.obj_permY1 = ObjectPermission.objects.\
            get_or_create_for_object_or_class("permY1", self.projectY)[0]
        self.obj_permY2 = ObjectPermission.objects.\
            get_or_create_for_object_or_class("permY2", self.projectY)[0]
        self.obj_permY3 = ObjectPermission.objects.\
            get_or_create_for_object_or_class("permY3", self.projectY)[0]
        self.obj_permY4 = ObjectPermission.objects.\
            get_or_create_for_object_or_class("permY4", self.projectY)[0]
        
        self.roleY1 = ProjectRole.objects.create(
            name="roleY1", project=self.projectY,
        )
        self.roleY1.obj_permissions.add(self.obj_permY1)
        
        self.roleY2 = ProjectRole.objects.create(
            name="roleY2", project=self.projectY,
        )
        self.roleY2.obj_permissions.add(self.obj_permY2)

        self.roleY3 = ProjectRole.objects.create(
            name="roleY3", project=self.projectY,
        )
        self.roleY3.obj_permissions.add(self.obj_permY1)
        self.roleY3.obj_permissions.add(self.obj_permY3)

    def test_give_to_permittee(self):
        # Give the role to a user and check that she gets the permission
        self.role1.give_to_permittee(self.u1)
        self.assertTrue(has_permission(self.u1, self.project, "perm1"))
        
        # check that delegation permissions are enforced
        self.assertRaises(
            PermissionCannotBeDelegated,
            self.role1.give_to_permittee,
            self.u2,
            giver=self.u1,
        )
        
        # Give another role to the user and check that she gets the permission
        self.role2.give_to_permittee(self.u1, can_delegate=True)
        self.assertTrue(has_permission(self.u1, self.project, "perm2"))
        
        # check that delegation permissions are enforced
        self.role2.give_to_permittee(
            self.u2,
            giver=self.u1,
        )
        self.assertTrue(has_permission(self.u1, self.project, "perm2"))
        
    def test_remove_from_permittee_no_conflict(self):
        """
        Check that a role can be removed from a permittee along with its
        permissions when no other roles give the same permission
        """
        
        self.role1.give_to_permittee(self.u1)
        self.assertTrue(has_permission(self.u1, self.project, "perm1"))

        self.role1.remove_from_permittee(self.u1)
        self.assertFalse(has_permission(self.u1, self.project, "perm1"))

    def test_remove_from_permittee_with_conflict(self):
        """
        Check that a role can be removed from a permittee along with its
        non-conflicting permissions
        """
        
        self.role1.give_to_permittee(self.u1)
        self.role3.give_to_permittee(self.u1)
        
        self.assertTrue(has_permission(self.u1, self.project, "perm1"))
        self.assertTrue(has_permission(self.u1, self.project, "perm3"))
        
        self.role1.remove_from_permittee(self.u1)
        self.assertTrue(has_permission(self.u1, self.project, "perm1"))
        self.assertTrue(has_permission(self.u1, self.project, "perm3"))

        self.role1.give_to_permittee(self.u1)
        self.role3.remove_from_permittee(self.u1)
        self.assertTrue(has_permission(self.u1, self.project, "perm1"))
        self.assertFalse(has_permission(self.u1, self.project, "perm3"))
        
    def test_add_permission(self):
        """
        Check that adding a permission to a role gives that permission to
        all permittees with the role
        """
        
        self.role1.give_to_permittee(self.u1)
        self.role1.give_to_permittee(self.u2)
        self.assertFalse(has_permission(self.u1, self.project, "perm2"))
        self.assertFalse(has_permission(self.u2, self.project, "perm2"))
        
        self.role1.add_permission(self.obj_perm2)
        self.assertTrue(has_permission(self.u1, self.project, "perm2"))
        self.assertTrue(has_permission(self.u2, self.project, "perm2"))
        
    def test_add_permission_delegation(self):
        """
        Checks that add_permission works, and that delegation permissions
        are enforced.
        """
        
        self.role1.give_to_permittee(self.u1)
        self.role1.add_permission(self.obj_perm2, can_delegate=True)
        self.role1.add_permission(self.obj_perm3, can_delegate=True)
        self.role2.give_to_permittee(self.u2, giver=self.u1)
        self.role2.add_permission(self.obj_perm3, giver=self.u1)
        self.assertTrue(has_permission(self.u2, self.project, "perm2"))
        self.assertTrue(has_permission(self.u2, self.project, "perm3"))
        
        # check when delegation does not work
        self.role2.add_permission(self.obj_perm4)
        self.assertTrue(has_permission(self.u2, self.project, "perm4"))
        self.assertRaises(
            PermissionCannotBeDelegated,
            self.role1.add_permission,
            self.obj_perm4,
            giver=self.u2
        )
    
    def test_filter_for_can_delegate(self):
        self.role3.give_to_permittee(self.u1, can_delegate=True)
        # check that the roles u1 can give are there
        givable_roles = ProjectRole.objects.filter_for_can_delegate(
            self.u1, self.project)
        self.assertTrue(
            self.role1 in givable_roles,
            "Expected role %s in givable roles, instead got %s" % 
                (self.role1, givable_roles))
        self.assertTrue(
            self.role3 in givable_roles,
            "Expected role %s in givable roles, instead got %s" % 
                (self.role3, givable_roles))
        self.assertEqual(givable_roles.count(), 2)
        
        # now add a permission to role1 without delegating
        self.role1.add_permission(self.obj_perm2)
        
        # The user shouldn't be able to delegate role1
        givable_roles = ProjectRole.objects.filter_for_can_delegate(
            self.u1, self.project)
        self.assertEqual(givable_roles.count(), 1)
        self.assertTrue(
            self.role3 in givable_roles,
            "Expected role %s in givable roles, instead got %s" % 
                (self.role3, givable_roles))
    
        # now add a permission to role3 without delegating
        self.role3.add_permission(self.obj_perm2)
        self.assertFalse(
            PermissionOwnership.objects.get_ownership(
                "perm2", self.project, self.u1).can_delegate)
        
        # The user shouldn't be able to delegate role3
        givable_roles = ProjectRole.objects.filter_for_can_delegate(
            self.u1, self.project)
        self.assertEqual(givable_roles.count(), 0)

    def test_remove_permission(self):
        """
        Check that a permission can be removed from a role with and
        without conflicts
        """
        self.role1.give_to_permittee(self.u1)
        self.role1.give_to_permittee(self.u2)
        self.role1.add_permission(self.obj_perm2)

        # remove with no conflict
        self.role1.remove_permission(self.obj_perm2)
        self.assertFalse(has_permission(self.u1, self.project, "perm2"))
        self.assertFalse(has_permission(self.u2, self.project, "perm2"))

        # add perm and conflicting role
        self.role2.give_to_permittee(self.u1)
        self.role2.give_to_permittee(self.u2)
        self.role1.add_permission(self.obj_perm2)
        self.assertTrue(has_permission(self.u1, self.project, "perm2"))
        self.assertTrue(has_permission(self.u2, self.project, "perm2"))
        
        # nothing should happen since role2 has "perm2"
        self.role1.remove_permission(self.obj_perm2)
        self.assertTrue(has_permission(self.u1, self.project, "perm2"))
        self.assertTrue(has_permission(self.u2, self.project, "perm2"))

    def test_filter_for_permission(self):
        """
        Check that the filter_for_permission method of the
        L{ProjectRoleManager} works.
        """
        roles = ProjectRole.objects.filter_for_permission(
            "perm1", self.project)
        self.assertEqual(roles.count(), 2)
        self.assertTrue(self.role1 in roles)
        self.assertTrue(self.role3 in roles)
        
    def test_get_users_for_role(self):
        self.role3.give_to_permittee(self.u1, can_delegate=True)
        self.role3.give_to_permittee(self.u2, can_delegate=False)
        self.role1.give_to_permittee(self.u3, can_delegate=True)
        
        users = get_users_for_role(self.role3, can_delegate=False)
        self.assertEqual(users.count(), 2)
        self.assertTrue(self.u1 in users)
        self.assertTrue(self.u2 in users)

        users = get_users_for_role(self.role3, can_delegate=True)
        self.assertEqual(users.count(), 1)
        self.assertTrue(self.u1 in users)

        users = get_users_for_role(self.role1, can_delegate=False)
        self.assertEqual(users.count(), 3)
        self.assertTrue(self.u1 in users)
        self.assertTrue(self.u2 in users)
        self.assertTrue(self.u3 in users)

        users = get_users_for_role(self.role1, can_delegate=True)
        self.assertEqual(users.count(), 2)
        self.assertTrue(self.u1 in users)
        self.assertTrue(self.u3 in users)
        