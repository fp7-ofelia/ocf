from django.db import models
from django.contrib import auth
from clearinghouse.security.models import AbstractSecureModel

class TestModel(AbstractSecureModel):
    '''
    A model that is used to test the security app.
    '''
    
    nonsecret = models.IntegerField(default=10)
    secret = models.IntegerField(default=100)
    
    writeable = models.IntegerField(default=30)
    limitedwriteable = models.IntegerField(default=40)

class TestModelChild(TestModel):
    '''
    A model that is used to test the security app.
    '''
    pass


class TestModelRole(AbstractTestModelRole):
    class AdminTestRole(AbstractTestModelRole.Role):
        '''
        Allow reading secret fields and full write access
        '''
        pass
    
class NormalModel(models.Model):
    pass

    
#class UserTestRole(SecurityRole):
#    '''
#    Limit reads to all except 'secret'. Only allow writes 
#    to 'limitedwriteable' if the value written is between 40 and 50.
#    '''
#
#    class Meta:
#        related_secure_model = SecureTestModel
#
#    def get_write_protected_fields(self, old_object):
#        '''
#        check that value for 'limitedwriteable' has not been change to
#        a value > 50 or < 40.
#        '''
#        if old_object.limitedwriteable != self._object.limitedwriteable \
#        and (self._object.limitedwriteable > 50 or
#             self._object.limitedwriteable < 40):
#            return ['limitedwriteable']
#        
#        return []
#        
#    def get_read_protected_fields(self):
#        '''
#        Do not allow reads to secret
#        '''
#        return ['secret']
#
#    def can_delete(self):
#        return False
#    
#    def can_add_role(self, user, role):
#        return False
#    
#    def can_delete_role(self, role):
#        return False
