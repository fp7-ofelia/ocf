from django import forms
import re
from openflow.optin_manager.admin_manager.models import AutoApproveServerProxy
from expedient.common.xmlrpc_serverproxy.forms import PasswordXMLRPCServerProxyFormHelperAddin
import logging

logger = logging.getLogger("AdminManagerForms")

class ScriptProxyForm(forms.ModelForm,
                        PasswordXMLRPCServerProxyFormHelperAddin):
    password2 = forms.CharField(label='Retype Password',
                                widget=forms.PasswordInput(render_value=False))
    
    class Meta:
        model = AutoApproveServerProxy
        widgets = {
            "password": forms.PasswordInput(),
        }
        fields = ["username", "password", "password2",
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

class MACAddressForm(forms.Field):
    def clean(self, value):
        if value == "*":
            return value
        else:
            pattern = re.compile(r"^([0-9a-fA-F]{1,2}[:-]){5}[0-9a-fA-F]{1,2}$")
            if (not pattern.match(value)):
                raise forms.ValidationError("Not a valid MAC Address")
        return value
    
class UserRegForm(forms.Form):
    mac_addr = MACAddressForm(initial = "*", label='Mac Address')
    ip_addr = forms.IPAddressField(label='IP Address')
    

