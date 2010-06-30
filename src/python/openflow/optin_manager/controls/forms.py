from django import forms
from django.contrib.auth.models import User
from django.forms.util import ErrorList
from django.forms import ModelForm
from openflow.optin_manager.xmlrpc_server.models import FVServerProxy

class FVServerForm(ModelForm):
    class Meta:
        model = FVServerProxy
        fields = ('name', 'url', 'max_password_age', 'verify_certs','username')
        

class FVServerFormPassword(forms.Form):
    password1 = forms.CharField(label='Password',
                            widget=forms.PasswordInput(render_value=False))
    password2 = forms.CharField(label='Retype Password',
                            widget=forms.PasswordInput(render_value=False)) 

    def clean(self):
        cleaned_data = self.cleaned_data
        if (cleaned_data.get("password1") != cleaned_data.get("password2")):
            self._errors["general"] = ErrorList(["Passwords don't match"])

class CHUserForm(forms.Form):
    username = forms.CharField(max_length = 100)
    password1 = forms.CharField(label='New Password',
                            widget=forms.PasswordInput(render_value=False)) 
    password2 = forms.CharField(label='Retype new password',
                            widget=forms.PasswordInput(render_value=False)) 
    def clean(self):
        cleaned_data = self.cleaned_data
        if (cleaned_data.get("password1") != cleaned_data.get("password2")):
            self._errors["general"] = ErrorList(["Passwords don't match"])

def pack_ch_user_info(chuser):
    result={}
    result["username"] = chuser.username
    result["password1"] = chuser.password
    result["password2"] = chuser.password
    return result