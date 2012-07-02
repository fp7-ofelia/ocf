'''
Created on Jun 10, 2010

@author: jnaous
'''
from django import forms
from django.contrib.auth.models import User
from models import PermissionUser, PermissionRequest

class PermissionRequestForm(forms.ModelForm):
    """
    A form that can be used to request a permission from another user.
    """
    
    class Meta:
        fields=["permission_owner", "message"]
        model = PermissionRequest
        
    def __init__(self, permission_owners_qs, *args, **kwargs):
        """
        Set the permission_owners queryset.
        """
        super(PermissionRequestForm, self).__init__(*args, **kwargs)
        self.fields["permission_owner"].queryset = permission_owners_qs
