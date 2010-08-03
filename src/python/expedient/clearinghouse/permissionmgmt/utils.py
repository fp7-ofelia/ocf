'''
Created on Aug 2, 2010

@author: jnaous
'''
from expedient.common.permissions.views import request_permission

def request_permission_wrapper(*args, **kwargs):
    return request_permission(
        template="permissionmgmt/request_permission.html")(*args, **kwargs)
