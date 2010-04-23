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


class TestModelRole(BaseTestModelRole):
    class Admin(BaseTestModelRole.Owner):
        '''
        Allow reading secret fields and full write access
        '''
        pass
    
    class User(BaseTestModelRole.AbstractRole):
        '''
        Limit reads to all except 'secret'. Only allow writes 
        to 'limitedwriteable' if the value written is between 40 and 50.
        '''
    
        @classmethod
        def get_write_protected_fields(cls, new_obj, old_obj):
            '''
            check that value for 'limitedwriteable' has not been change to
            a value > 50 or < 40.
            '''
            if old_obj.limitedwriteable != new_obj.limitedwriteable \
            and (new_obj.limitedwriteable > 50 or
                 new_obj.limitedwriteable < 40):
                return ['limitedwriteable']
            
            return []
        
        @classmethod
        def get_read_protected_fields(cls, obj):
            return ['secret']
        
        @classmethod
        def can_delete(cls, obj):
            return False
        
        @classmethod
        def can_write(cls, obj):
            return True
                    
        @classmethod
        def can_add_role(cls, obj, role, rcv_user):
            return False
        
        @classmethod
        def can_del_role(cls, obj, role, rcv_user):
            return False
