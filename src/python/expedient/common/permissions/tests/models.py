'''
Created on Jun 9, 2010

@author: jnaous
'''
from django.db import models
from ..decorators import require_obj_permissions_for_method
from expedient.common.middleware import threadlocals

def user_parse_func(request):
    return request.user
threadlocals.add_parser("user_kw", user_parse_func)

def test_parse_func(request):
    try:
        return PermissionTestClass.objects.all()[0]
    except:
        return None
threadlocals.add_parser("test_kw", test_parse_func)

class PermissionTestClass(models.Model):
    """
    Dummy class used for tests.
    """

    val = models.IntegerField()
    
    @require_obj_permissions_for_method(
        "user_kw", ["can_get_x2", "can_read_val"])
    def get_val_x2(self):
        return self.val * 2
    
    @require_obj_permissions_for_method("user_kw", ["can_get_x3"])
    def get_val_x3_other_val(self):
        return (self.val * 3)
    
    @require_obj_permissions_for_method("test_kw", ["can_get_x4"])
    def get_val_x4(self):
        return self.val * 4
    
    @require_obj_permissions_for_method(
        "user_kw", ["can_get_x5", "can_read_val"])
    def get_val_x5_username(self):
        return self.val * 5
