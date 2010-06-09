'''
Created on Jun 9, 2010

@author: jnaous
'''
from django.db import models
from ..decorators import require_obj_permissions, require_obj_permissions_for_user

class PermissionTestClass(models.Model):
    """
    Dummy class used for tests.
    """

    val = models.IntegerField()
    
    @require_obj_permissions("user_kw", ["can_get_x2", "can_read_val"], True)
    def get_val_x2(self):
        return self.val * 2
    
    @require_obj_permissions("user_kw", ["can_get_x3"], False)
    def get_val_x3_other_val(self, user_kw=None):
        return (self.val * 3, user_kw)
    
    @require_obj_permissions("test_kw", ["can_get_x4"])
    def get_val_x4(self):
        return self.val * 4
    
    @require_obj_permissions_for_user(["can_get_x5", "can_read_val"], False)
    def get_val_x5_username(self, user=None):
        return (self.val * 5, user.username)
