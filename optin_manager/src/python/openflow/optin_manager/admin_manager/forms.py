from django import forms
import re
from openflow.optin_manager.admin_manager.models import AutoApproveServerProxy
from openflow.optin_manager.admin_manager.models import FlowSpaceAutoApproveScript
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

class FlowSpaceAutoApproveScriptForm(forms.ModelForm):
    class Meta:
        model = FlowSpaceAutoApproveScript
#        vlan_auto_grant = forms.CheckboxInput(check_test=lambda value: value == True)
#        flowspace_auto_approval = forms.CheckboxInput()
        widgets = {
            "vlan_auto_grant": forms.CheckboxInput(),
            "flowspace_auto_approval": forms.CheckboxInput(),
        }
        fields = ["vlan_auto_grant", "flowspace_auto_approval"]
    
#    def __init__(self):
#        self.fields["vlan_auto_grant"].initial = True
#        self.fields["flowspace_auto_approval"].initial = True
    
    def clean(self):
        # check passwords first
        logger.debug("Checking option checked")
        vlan_auto_grant = self.cleaned_data["vlan_auto_grant"]
        flowspace_auto_approval = self.cleaned_data["flowspace_auto_approval"]
        # One should not be set without the other
        if flowspace_auto_approval and not vlan_auto_grant:
            raise forms.ValidationError("You should provide automatic VLAN granting for automatic Flowspace approval")
        return self.cleaned_data

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
    

