'''
Created on Dec 3, 2009

@author: jnaous
'''

from django import forms
from models import UserProfile
from django.contrib.auth.models import User
from django.contrib.auth.forms import AdminPasswordChangeForm

class UserProfileForm(forms.ModelForm):
    '''
    A form for editing UserProfiles that can be set to either show
    or hide some admin fields by setting the IS_ADMIN keyword arg
    '''
    
    class Meta:
        model = UserProfile
        exclude = ('user', 'created_by',)

    def __init__(self, *args, **kwargs):
        IS_ADMIN='is_admin'
        is_admin = IS_ADMIN in kwargs and kwargs[IS_ADMIN]
        if is_admin: del kwargs[IS_ADMIN]

        super(UserProfileForm, self).__init__(*args, **kwargs)
        
        if not is_admin:
            for field in ('is_aggregate_admin', 'is_clearinghouse_admin'):
                del self.fields[field]

class UserForm(forms.ModelForm):
    '''
    A form for editing User that can be set to either show
    or hide some admin fields by setting the IS_ADMIN keyword arg
    '''
    
    class Meta:
        model = User
        exclude = ('username', 'password', 'last_login', 'date_joined', 'groups', 'user_permissions')

    def __init__(self, *args, **kwargs):
        IS_ADMIN='is_admin'
        is_admin = IS_ADMIN in kwargs and kwargs[IS_ADMIN]
        if is_admin: del kwargs[IS_ADMIN]

        super(UserProfileForm, self).__init__(*args, **kwargs)
        
        if not is_admin:
            for field in ('is_staff', 'is_superuser', ):
                del self.fields[field]

class SelectResearcherForm(forms.Form):
    '''
    A form that shows a choice to select researchers only.
    '''
    researcher_profile = forms.ModelChoiceField(UserProfile.objects.filter(is_researcher=True), label="Owner")

class AdminPasswordChangeFormDisabled(AdminPasswordChangeForm):
    '''
    A form used to change the password of a user in the admin interface, with
    the password fields shown disabled initially.
    '''
    
    def __init__(self, *args, **kwargs):
        super(AdminPasswordChangeFormDisabled, self).__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs['disabled'] = True
        self.fields['password2'].widget.attrs['disabled'] = True
