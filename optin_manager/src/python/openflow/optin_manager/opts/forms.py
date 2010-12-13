from django import forms
from openflow.optin_manager.flowspace.utils import dotted_ip_to_int, mac_to_int
from django.forms.util import ErrorList
import re
from openflow.optin_manager.opts.models import AdminFlowSpace    

class MACAddressForm(forms.Field):
    def clean(self, value):
        pattern = re.compile(r"^([0-9a-fA-F]{1,2}[:-]){5}[0-9a-fA-F]{1,2}$")
        if (not pattern.match(value)):
            raise forms.ValidationError("Not a valid MAC Address")
        return value
            

class UploadFileForm(forms.Form):
    file  = forms.FileField(label="Add Rules from File:")


class AdminOptInForm(forms.Form):
    
    mac_from_s    = MACAddressForm(initial = "00:00:00:00:00:00")
    mac_from_e    = MACAddressForm(initial = "FF:FF:FF:FF:FF:FF")
    mac_to_s      = MACAddressForm(initial = "00:00:00:00:00:00")
    mac_to_e      = MACAddressForm(initial = "FF:FF:FF:FF:FF:FF")
    eth_type_s    = forms.IntegerField(max_value = 0xFFFF, initial = 0)
    eth_type_e    = forms.IntegerField(max_value = 0xFFFF, initial = 0xFFFF)

    vlan_id_s   = forms.IntegerField(max_value = 4095, initial = 0)
    vlan_id_e   = forms.IntegerField(max_value = 4095, initial = 4095)

    
    ip_from_s   = forms.IPAddressField(initial = "0.0.0.0")
    ip_from_e   = forms.IPAddressField(initial = "255.255.255.255")
    ip_to_s     = forms.IPAddressField(initial = "0.0.0.0")
    ip_to_e     = forms.IPAddressField(initial = "255.255.255.255")
    
    ip_proto_s  = forms.IntegerField(max_value = 255, initial = 0)  
    ip_proto_e  = forms.IntegerField(max_value = 255, initial = 255)

    tp_from_s   = forms.IntegerField(max_value = 0xFFFF, initial = 0)  
    tp_from_e  = forms.IntegerField(max_value = 0xFFFF, initial = 0xFFFF)
    tp_to_s  = forms.IntegerField(max_value = 0xFFFF, initial = 0)  
    tp_to_e  = forms.IntegerField(max_value = 0xFFFF, initial = 0xFFFF)
    
    def clean(self):
        if self._errors:
            return self.cleaned_data
        cleaned_data = self.cleaned_data
        self.saved_cleaned_data = cleaned_data
        mac_from_s = cleaned_data.get("mac_from_s")
        mac_from_e = cleaned_data.get("mac_from_e")
        mac_to_s = cleaned_data.get("mac_to_s")
        mac_to_e = cleaned_data.get("mac_to_e")
        eth_type_s = cleaned_data.get("eth_type_s")
        eth_type_e = cleaned_data.get("eth_type_e")
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
        if (mac_to_int(mac_from_s) > mac_to_int(mac_from_e)):
            raise forms.ValidationError("Empty Source MAC Range")
        if (mac_to_int(mac_to_s) > mac_to_int(mac_to_e)):
            raise forms.ValidationError("Empty Destination MAC Range")
        if (eth_type_s > eth_type_e):
            raise forms.ValidationError("Empty Ethernet Type Range")
        if (vlan_id_s > vlan_id_e):
            raise forms.ValidationError("Empty VLAN Range")
        if (dotted_ip_to_int(ip_from_s) > dotted_ip_to_int(ip_from_e)):
            raise forms.ValidationError("Empty Source IP Range")
        if (dotted_ip_to_int(ip_to_s) > dotted_ip_to_int(ip_to_e)):
            raise forms.ValidationError("Empty Destination IP Range")
        if (ip_proto_s > ip_proto_e):
            raise forms.ValidationError("Empty IP Protocol Range")
        if (tp_from_s > tp_from_e):
            raise forms.ValidationError("Empty Source Transport Port Range")
        if (tp_to_s > tp_to_e):
            raise forms.ValidationError("Empty Destination Transport Port Range")
            
        return cleaned_data
    
    def get_flowspace(self,FS_Object):
        cleaned_data = self.saved_cleaned_data
        if self._errors:
            return None
        
        return FS_Object(
            mac_src_s = mac_to_int(cleaned_data.get("mac_from_s")),
            mac_src_e = mac_to_int(cleaned_data.get("mac_from_e")),
            mac_dst_s = mac_to_int(cleaned_data.get("mac_to_s")),
            mac_dst_e = mac_to_int(cleaned_data.get("mac_to_e")),
            eth_type_s = int(cleaned_data.get("eth_type_s")),
            eth_type_e = int(cleaned_data.get("eth_type_e")),
            vlan_id_s = int(cleaned_data.get("vlan_id_s")),
            vlan_id_e = int(cleaned_data.get("vlan_id_e")),
            ip_src_s = dotted_ip_to_int(cleaned_data.get("ip_from_s")),
            ip_src_e = dotted_ip_to_int(cleaned_data.get("ip_from_e")),
            ip_dst_s = dotted_ip_to_int(cleaned_data.get("ip_to_s")),
            ip_dst_e = dotted_ip_to_int(cleaned_data.get("ip_to_e")),
            ip_proto_s = int(cleaned_data.get("ip_proto_s")),
            ip_proto_e = int(cleaned_data.get("ip_proto_e")),
            tp_src_s = int(cleaned_data.get("tp_from_s")),
            tp_src_e = int(cleaned_data.get("tp_from_e")),
            tp_dst_s = int(cleaned_data.get("tp_to_s")),
            tp_dst_e = int(cleaned_data.get("tp_to_e")),
        ) 
            
    
