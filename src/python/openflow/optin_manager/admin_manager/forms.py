from django import forms
import re

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
