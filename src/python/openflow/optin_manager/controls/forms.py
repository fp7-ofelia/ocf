from django import forms
from django.contrib.auth.models import User
from django.forms.util import ErrorList
from django.forms import ModelForm
from openflow.optin_manager.xmlrpc_server.models import FVServerProxy
from expedient.common.xmlrpc_serverproxy.forms import PasswordXMLRPCServerProxyFormHelperAddin
import logging

logger = logging.getLogger("ControlsForms")

#class FVServerForm(ModelForm):
#    class Meta:
#        model = FVServerProxy
#        fields = ('name', 'url', 'max_password_age', 'verify_certs','username')
#        
#
#class FVServerFormPassword(forms.Form):
#    password1 = forms.CharField(label='Password',
#                            widget=forms.PasswordInput(render_value=False))
#    password2 = forms.CharField(label='Retype Password',
#                            widget=forms.PasswordInput(render_value=False)) 
#
#    def clean(self):
#        cleaned_data = self.cleaned_data
#        if (cleaned_data.get("password1") != cleaned_data.get("password2")):
#            self._errors["general"] = ErrorList(["Passwords don't match"])

class FVServerProxyForm(forms.ModelForm,
                        PasswordXMLRPCServerProxyFormHelperAddin):
    password2 = forms.CharField(label='Retype Password',
                                widget=forms.PasswordInput(render_value=False))
    
    class Meta:
        model = FVServerProxy
        widgets = {
            "password": forms.PasswordInput(),
        }
        fields = ["name", "username", "password", "password2",
                  "max_password_age", "url", "verify_certs"]
        
    def clean(self):
        # check passwords first
        logger.debug("Checking passwords")
        p1 = self.cleaned_data["password"]
        try:
            p2 = self.cleaned_data["password2"]
        except:
            p2 = None
        if p1 != p2:
            logger.debug("Passwords don't match")
            raise forms.ValidationError("Passwords do not match. Re-enter password.")
        return PasswordXMLRPCServerProxyFormHelperAddin.clean(self)

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