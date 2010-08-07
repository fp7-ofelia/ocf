from django import forms
from django.contrib.auth.models import User
from openflow.optin_manager.users.models import UserProfile
from openflow.optin_manager.xmlrpc_server.models import FVServerProxy
from expedient.common.xmlrpc_serverproxy.forms import PasswordXMLRPCServerProxyFormHelperAddin
import logging

logger = logging.getLogger("ControlsForms")

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
            logger.debug("Passwords don't match")
            raise forms.ValidationError("Passwords do not match. Re-enter password")
        
        username_cleaned = cleaned_data.get("username")
        ch_users = UserProfile.objects.filter(is_clearinghouse_user=True)
        if ch_users.count() > 0:
            ch_id = ch_users[0].id
            same_uname = User.objects.filter(username = username_cleaned).exclude(id = ch_id)
        else:
            same_uname = User.objects.filter(username = username_cleaned)

        if (same_uname.count() > 0):
            raise forms.ValidationError("Clearinghouse username already exist in system. Please enter a unique username")

def pack_ch_user_info(chuser):
    result={}
    result["username"] = chuser.username
    result["password1"] = chuser.password
    result["password2"] = chuser.password
    return result