'''
Created on Feb 26, 2010

@author: jnaous
'''

from clearinghouse.security_tester.models import SecureTestModel, AdminTestRole,\
    UserTestRole
from clearinghouse.middleware import threadlocals
from django.contrib.auth.models import User
from clearinghouse.security.models import SecureModel, OwnerSecurityRole,\
    SecurityRole

class TestAll(object):
    
    def setUp(self):
        self.owner = User.objects.create_user('owneruser', 'email@bla.com', 'password')
        self.user = User.objects.create_user('testuser', 'email@bla.com', 'password')
        threadlocals.push_current_user(self.owner)
        self.admin_test_model = SecureTestModel.objects.create()
        self.user_test_model = SecureTestModel.objects.create()
        self.roleless_test_model = SecureTestModel.objects.create()
        
#        print "++++++"
#        roles = SecurityRole.objects.all()
#        owner_roles = OwnerSecurityRole.objects.all()
#        print "roles: %s" % roles
#        for r in roles:
#            r = r.as_leaf_class()
#            print r
#        print "ownerroles: %s" % owner_roles
#        for r in owner_roles:
#            print r.__dict__
        self.admin_test_role = AdminTestRole.objects.create(_user=self.user, _object=self.admin_test_model)
        self.user_test_role = UserTestRole.objects.create(_user=self.user, _object=self.user_test_model)
        threadlocals.push_current_user(self.user)
        print "******* Done SetUp"
        
    def test_ownership(self):
        '''Check that the owner is given ownership roles'''
        print self.owner.security_roles.all().count()
        
        for r in self.owner.security_roles.all():
            r = r.as_leaf_class()
            print r.__class__
        
    def test_protect_roleless_obj(self):
        '''Tests that objects that do not have a role for the current user are
        not seen in the returned querysets.'''
        
        seen_set = set(SecureTestModel.objects.all().values_list('pk', flat=True))
        wanted_set = set([self.admin_test_model.pk, self.user_test_model.pk])
        print 'Saw %s. Expected %s' % (seen_set, wanted_set)
        
    def test_nonsecret_reads(self):
        '''Tests that non-secret field can be read by all'''
        
        obj = SecureTestModel.objects.get(pk=self.admin_test_model.pk)
        self.assertEqual(self.admin_test_model.nonsecret,
                         obj.nonsecret,
                         'Did not get correct value for non-secret field')

        obj = SecureTestModel.objects.get(pk=self.user_test_model.pk)
        self.assertEqual(self.user_test_model.nonsecret,
                         obj.nonsecret,
                         'Did not get correct value for non-secret field')

    def test_unlimited_writes(self):
        '''Tests that we can write to a field that has no write restrictions'''
        
        self.admin_test_model.writeable = 100
        self.admin_test_model.save()
        
        obj = SecureTestModel.objects.get(pk=self.admin_test_model.pk)
        self.assertEqual(100,
                         obj.writeable,
                         'Did not store the correct value for writeable field.')
        
    def test_allowed_limited_write(self):
        '''Tests that we can write allowed values into a write protected field'''
        
        obj = SecureTestModel.objects.get(pk=self.user_test_model.pk)
        obj.limitedwriteable = 45
        obj.save()
#        self.user_test_model.limitedwriteable = 45
#        self.user_test_model.save()

        obj = SecureTestModel.objects.get(pk=self.user_test_model.pk)
        
        return obj
#        self.assertEqual(45,
#                         obj.limitedwriteable,
#                         'Did not store the correct value for limitedwriteable field.')
        
    def test_disallowed_limited_write(self):
        '''Tests that a security exception is raised if we try to write
        a protected field with an unallowed value.'''

        self.user_test_model.limitedwriteable = 10
        self.assertRaises(SecureTestModel.SecurityException,
                          self.user_test_model.save)

        obj = SecureTestModel.objects.get(pk=self.user_test_model.pk)
        self.assertEqual(40,
                         obj.limitedwriteable,
                         'Did not store the correct value for limitedwriteable field.')
        
