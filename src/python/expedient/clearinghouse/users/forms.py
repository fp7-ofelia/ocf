'''
Created on Dec 3, 2009

@author: jnaous
'''

from django import forms
from models import UserProfile
from django.contrib.auth.models import User
from django.contrib.auth.forms import AdminPasswordChangeForm, PasswordChangeForm
from registration.forms import RegistrationForm

class UserProfileForm(forms.ModelForm):
    '''
    A form for editing UserProfiles
    '''
    
    class Meta:
        model = UserProfile
        exclude = ('user')

class UserForm(forms.ModelForm):
    '''
    A form for editing Users
    '''
    class Meta:
        model = User
        exclude = ('username', 'password', 'last_login',
                   'date_joined', 'groups', 'user_permissions',
                   'is_superuser', 'is_staff', 'is_active')

class FullRegistrationForm(RegistrationForm):
    first_name = forms.CharField(max_length=40)
    last_name = forms.CharField(max_length=40)
    affiliation = forms.CharField(
        max_length=100,
        help_text="The organization that you are affiliated with.")
    
    def save(self, profile_callback=None):
        user = super(FullRegistrationForm, self).save(
            profile_callback=profile_callback)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.save()
        
        UserProfile.objects.create(
            user=user, affiliation=self.cleaned_data["affiliation"])
        
        return user

class AdminPasswordChangeFormDisabled(AdminPasswordChangeForm):
    '''
    A form used to change the password of a user in the admin interface, with
    the password fields shown disabled initially.
    '''
    
    def __init__(self, *args, **kwargs):
        super(AdminPasswordChangeFormDisabled, self).__init__(*args, **kwargs)
        for field in ['password1', 'password2']:
            self.fields[field].widget.attrs['disabled'] = True

class PasswordChangeFormDisabled(PasswordChangeForm):
    '''
    A form used to change the password of a user, with
    the password fields shown disabled initially. Requires confirmation
    with the old password
    '''
    
    def __init__(self, *args, **kwargs):
        super(PasswordChangeFormDisabled, self).__init__(*args, **kwargs)
        for field in ['old_password', 'new_password1', 'new_password2']:
            self.fields[field].widget.attrs['disabled'] = True
