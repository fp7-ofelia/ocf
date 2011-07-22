from vt_manager.models.NetworkInterface import NetworkInterface
from django import forms
from vt_manager.utils.EthernetUtils import EthernetUtils

class NetworkInterfaceForm(forms.ModelForm):
    '''
    A form for editing NetorkInterfaces
    '''
    class Meta:
        model = NetworkInterface
        exclude = ('isMgmt', 'isBridge', 'mac',
                   'ip4s', 'connectedTo')

	mac = forms.CharField(max_length = 17, validators=[EthernetUtils.checkValidMac])


class MgmtBridgeForm(forms.Form):

	name = forms.CharField(max_length=40, label = "Name")
	mac = forms.CharField(max_length = 17, label = "MAC Address", validators=[EthernetUtils.checkValidMac], required = False)
