from django import forms
from django.contrib.auth.models import User
from django.forms.util import ErrorList

class FVServerForm(forms.Form):
    name = forms.CharField(max_length = 40)
    url = forms.URLField()
    username = forms.CharField(max_length = 100)
    password = forms.CharField(label='password',
                            widget=forms.PasswordInput(render_value=False)) 
    max_password_age = forms.IntegerField(max_value = 3650)
    verify_certs = forms.BooleanField(required=False)
    
def pack_fvserver_info(fvserverp):
    result={}
    result["name"] = fvserverp.name
    result["username"] = fvserverp.username
    result["password"] = fvserverp.password
    result["url"] = fvserverp.url
    result["max_password_age"] = fvserverp.max_password_age
    result["verify_certs"] = fvserverp.verify_certs
    return result

class CHUserForm(forms.Form):
    username = forms.CharField(max_length = 100)
    password1 = forms.CharField(label='Password',
                            widget=forms.PasswordInput(render_value=False)) 
    password2 = forms.CharField(label='Retype password',
                            widget=forms.PasswordInput(render_value=False)) 
    def clean(self):
        cleaned_data = self.cleaned_data
        if (cleaned_data.get("password1") != cleaned_data.get("password2")):
            self._errors["passwords"] = ErrorList("Passwords don't match")
            
def pack_ch_user_info(chuser):
    result={}
    result["username"] = chuser.username
    result["password1"] = chuser.password
    result["password2"] = chuser.password
    return result