from django.db import models
from clearinghouse.security.models import SecurityRole, SecureModel

class SecretIntModel(SecureModel):
    secret = models.IntegerField(default=20)

class SecureTestModel(SecureModel):
    '''
    A model that is used to test the security app.
    '''
    
    nonsecret = models.IntegerField(default=10)
    secret1 = models.OneToOneField(SecretIntModel)
    secret2 = models.IntegerField(default=100)
    
    writeable = models.IntegerField(default=30)
    limitedwriteable = models.IntegerField(default=40)

class AdminTestRole(SecurityRole):
    '''
    Allow reading secret fields and full write access
    '''
    
    def get_write_protected_fields(self, old_object):
        '''
        Allow any write.
        '''
        return []
    
    def get_read_protected_fields(self):
        '''
        Allow any read.
        '''
        return []
    
class UserTestRole(SecurityRole):
    '''
    Limit reads to all except 'secret'. Only allow writes 
    to 'limitedwriteable' if the value written is between 40 and 50.
    '''
    
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

