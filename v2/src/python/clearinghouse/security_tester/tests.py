"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from clearinghouse.security_tester.models import TestModel, TestModelRole, BaseTestModelRole
from clearinghouse.middleware import threadlocals
from django.contrib.auth.models import User

class TestAll(TestCase):
    
    def setUp(self):
        self.owner = User.objects.create_user('owneruser', 'email@bla.com', 'password')
        self.user = User.objects.create_user('testuser', 'email@bla.com', 'password')
        threadlocals.push_current_user(self.owner)
        self.admin_test_model = TestModel.objects.create()
        self.user_test_model = TestModel.objects.create()
        self.roleless_test_model = TestModel.objects.create()
        
        self.admin_test_role = TestModelRole.objects.create(
            security_user=self.user,
            security_object=self.admin_test_model,
            security_role_choice='Admin')
        self.user_test_role = TestModelRole.objects.create(
            security_user=self.user,
            security_object=self.admin_test_model,
            security_role_choice='User')
        threadlocals.push_current_user(self.user)
        print "******* Done SetUp"

    def test_setup(self):
        '''This tests always passes. Makes sure the setup goes OK'''
        pass
        
    def test_ownership(self):
        '''Check that the owner is given ownership roles'''
        self.assertEqual(self.owner.security_testmodel_roles.all().count(),
            3, 'owner does not have three roles.')
        
        for r in self.owner.security_testmodel_roles.all():
            self.assertEqual(r.security_role_choice, 'Owner', 'Owner has non-ownership role!')
        
        
#    def test_protect_roleless_obj(self):
#        '''Tests that objects that do not have a role for the current user are
#        not seen in the returned querysets.'''
#        
#        seen_set = set(SecureTestModel.objects.all().values_list('pk', flat=True))
#        wanted_set = set([self.admin_test_model.pk, self.user_test_model.pk])
#        self.assertEqual(seen_set, wanted_set, 'Saw %s. Expected %s' % (seen_set, wanted_set))
#        
#        self.assertRaises(SecureTestModel.DoesNotExist,
#                          SecureTestModel.objects.get,
#                          pk=self.roleless_test_model.pk)
#        
#    def test_nonsecret_reads(self):
#        '''Tests that non-secret field can be read by all'''
#        
#        obj = SecureTestModel.objects.get(pk=self.admin_test_model.pk)
#        self.assertEqual(self.admin_test_model.nonsecret,
#                         obj.nonsecret,
#                         'Did not get correct value for non-secret field')
#
#        obj = SecureTestModel.objects.get(pk=self.user_test_model.pk)
#        self.assertEqual(self.user_test_model.nonsecret,
#                         obj.nonsecret,
#                         'Did not get correct value for non-secret field')
#
#    def test_unlimited_writes(self):
#        '''Tests that we can write to a field that has no write restrictions'''
#        
#        self.admin_test_model.writeable = 100
#        self.admin_test_model.save()
#        
#        obj = SecureTestModel.objects.get(pk=self.admin_test_model.pk)
#        self.assertEqual(100,
#                         obj.writeable,
#                         'Did not store the correct value for writeable field.')
#        
#    def test_allowed_limited_write(self):
#        '''Tests that we can write allowed values into a write protected field'''
#        
#        obj = SecureTestModel.objects.get(pk=self.user_test_model.pk)
#        obj.limitedwriteable = 45
#        obj.save()
##        self.user_test_model.limitedwriteable = 45
##        self.user_test_model.save()
#
#        obj = SecureTestModel.objects.get(pk=self.user_test_model.pk)
#        self.assertEqual(45,
#                         obj.limitedwriteable,
#                         'Did not store the correct value for limitedwriteable field.')
#        
#    def test_disallowed_limited_write(self):
#        '''Tests that a security exception is raised if we try to write
#        a protected field with an unallowed value.'''
#
#        self.user_test_model.limitedwriteable = 10
#        self.assertRaises(SecureTestModel.SecurityException,
#                          self.user_test_model.save)
#
#        obj = SecureTestModel.objects.get(pk=self.user_test_model.pk)
#        self.assertEqual(40,
#                         obj.limitedwriteable,
#                         'Did not store the correct value for limitedwriteable field.')
        
