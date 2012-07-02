from django import forms
from django.contrib.auth.models import User

class UserForm(forms.ModelForm):
    '''
    A form for editing Users
    '''
    class Meta:
        model = User
        exclude = ('username', 'password', 'last_login', 'date_joined', 'groups', 'user_permissions',
                   'is_staff', 'is_superuser', 'is_active')
        
