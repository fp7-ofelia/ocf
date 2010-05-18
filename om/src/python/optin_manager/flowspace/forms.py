from django import forms
from optin_manager.flowspace.utils import dotted_ip_to_int
from django.forms.util import ErrorList
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
            

class AdminOptInForm(forms.Form):
    
    mac_from    = MACAddressForm(initial = "*")
    mac_to      = MACAddressForm(initial = "*")
    
    vlan_id_s   = forms.IntegerField(max_value = 4095, initial = 0)
    vlan_id_e   = forms.IntegerField(max_value = 4095, initial = 4095)

    
    ip_from_s   = forms.IPAddressField()
    ip_from_e   = forms.IPAddressField()
    ip_to_s     = forms.IPAddressField()
    ip_to_e     = forms.IPAddressField()
    
    ip_proto_s  = forms.IntegerField(max_value = 255, initial = 0)  
    ip_proto_e  = forms.IntegerField(max_value = 255, initial = 255)

    tp_from_s   = forms.IntegerField(max_value = 0xFFFF, initial = 0)  
    tp_from_e  = forms.IntegerField(max_value = 0xFFFF, initial = 0xFFFF)
    tp_to_s  = forms.IntegerField(max_value = 0xFFFF, initial = 0)  
    tp_to_e  = forms.IntegerField(max_value = 0xFFFF, initial = 0xFFFF)

    priority    = forms.IntegerField()
    
    def clean(self):
        cleaned_data = self.cleaned_data
        vlan_id_s = cleaned_data.get("vlan_id_s")
        vlan_id_e = cleaned_data.get("vlan_id_e")
        ip_from_s = cleaned_data.get("ip_from_s")
        ip_from_e = cleaned_data.get("ip_from_e")
        ip_to_s = cleaned_data.get("ip_to_s")
        ip_to_e = cleaned_data.get("ip_to_e")
        ip_proto_s = cleaned_data.get("ip_proto_s")
        ip_proto_e = cleaned_data.get("ip_proto_e")
        tp_from_s = cleaned_data.get("tp_from_s")
        tp_from_e = cleaned_data.get("tp_from_e")
        tp_to_s = cleaned_data.get("tp_to_s")
        tp_to_e = cleaned_data.get("tp_to_e")
        if (vlan_id_s > vlan_id_e):
            self._errors["vlan_id_s"] = ErrorList(["Empty VLAN Range"])
        if (dotted_ip_to_int(ip_from_s) > dotted_ip_to_int(ip_from_e)):
            self._errors["ip_from_s"] = ErrorList(["Empty IP Range"])
        if (dotted_ip_to_int(ip_to_s) > dotted_ip_to_int(ip_to_e)):
            self._errors["ip_to_s"] = ErrorList(["Empty IP Range"])
        if (ip_proto_s > ip_proto_e):
            self._errors["ip_proto_s"] = ErrorList(["Empty IP Protocol Range"])
        if (tp_from_s > tp_from_e):
            self._errors["tp_from_s"] = ErrorList(["Empty Transport Port Range"])
        if (tp_to_s > tp_to_e):
            self._errors["tp_to_s"] = ErrorList(["Empty Transport Port Range"])
            
    