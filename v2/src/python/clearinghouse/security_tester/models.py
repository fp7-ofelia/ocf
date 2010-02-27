from django.db import models
from clearinghouse.security.models import SecurityRole, SecureModel,\
    OwnerSecurityRole
from django.contrib import auth

class SecureTestModel(SecureModel):
    '''
    A model that is used to test the security app.
    '''
    
    nonsecret = models.IntegerField(default=10)
    secret = models.IntegerField(default=100)
    
    writeable = models.IntegerField(default=30)
    limitedwriteable = models.IntegerField(default=40)

class SecureTestModel2(SecureTestModel):
    '''
    A model that is used to test the security app.
    '''
    pass

class AdminTestRole(OwnerSecurityRole):
    '''
    Allow reading secret fields and full write access
    '''

    class Meta:
        related_secure_model = SecureTestModel
    
class UserTestRole(SecurityRole):
    '''
    Limit reads to all except 'secret'. Only allow writes 
    to 'limitedwriteable' if the value written is between 40 and 50.
    '''

    class Meta:
        related_secure_model = SecureTestModel

    def get_write_protected_fields(self, old_object):
        '''
        check that value for 'limitedwriteable' has not been change to
        a value > 50 or < 40.
        '''
        if old_object.limitedwriteable != self._object.limitedwriteable \
        and (self._object.limitedwriteable > 50 or
             self._object.limitedwriteable < 40):
            return ['limitedwriteable']
        
        return []
        
    def get_read_protected_fields(self):
        '''
        Do not allow reads to secret
        '''
        return ['secret']

    def can_delete(self):
        return False
    
    def can_add_role(self, user, role):
        return False
    
    def can_delete_role(self, role):
        return False
