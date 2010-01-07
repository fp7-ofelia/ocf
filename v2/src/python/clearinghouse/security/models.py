from django.db import models
from django.contrib import auth
from pyanno import abstractMethod, parameterTypes, returnType, selfType
from clearinghouse.middleware import threadlocals
from django.db.models.signals import post_init

class ObjectFieldPermission(object):
    '''
    Base abstract class for field permissions.
    '''
    
    @parameterTypes(selfType)
    @returnType(bool)
    def can_read(self):
        '''
        Checks whether the user can read the field's value
        '''
        return True

    @parameterTypes(selfType, object, object)
    @returnType(bool)
    def can_write(self, old_value, new_value):
        '''
        Checks whether the user can change the value of the field
        from old_value to new_value
        '''
        return True

class UserProfileAffiliationReadOnlyPermission(ObjectFieldPermission):
    '''
    Only allow reading the affiliation field.
    '''
    
    def can_read(self, value):
        return True
    
    def can_write(self, old_value, new_value):
        return False


def check_reads(sender, **kwargs):
    '''
    Check if the object id is in the DB, and delete the fields
    the user is not allowed to see. 
    '''
    print "*************\npost init signal:"
    print "kwargs: %s" % kwargs
    print "user: %s\n\n" % threadlocals.get_current_user()
post_init.connect(check_init)

class SecureModel(models.Model):
    pass

class ObjectSecurity(models.Model):
    '''
    Creates the hooks that are needed to police access. Accesses
    to all objects are mediated through objects that extend
    from ObjectSecurity.
    '''
    
    _user = models.ForeignKey(auth.models.User)
    _object = models.ForeignKey(SecureModel)
    
class PermissionField(models.CharField):
    '''
    A model field to be used in ObjectSecurity classes to define
    the permissions on model fields in the secured object.
    '''
    
    description = "Permissions on the field"
    
    def __init__(self, *args, **kwargs):
        if 'max_length' not in kwargs:
            kwargs['max_length'] = 200
    
    @abstractMethod
    def can_read(self, user):
        pass
    
    

class UserProfileSecurity(ObjectSecurity):
    '''
    Defines the security policy of the UserProfile objects
    '''
    pass

#    is_aggregate_admin = models.CharField(
#        max_length=200, choices={'readwrite': {'can_read': 'always_true',
#                                               'can_write': 'always_true',
#                                               },
#                                 'read'     : {'can_read': 'always_true',
#                                               'can_write': 'always_false',
#                                               },
#                                 }
#        )
#    
