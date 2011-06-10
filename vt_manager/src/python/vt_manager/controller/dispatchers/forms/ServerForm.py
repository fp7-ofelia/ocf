from vt_manager.models.VTServer import VTServer
from django import forms
from vt_manager.utils.EthernetUtils import EthernetUtils

class ServerForm(forms.ModelForm):
	'''
	A form for editing NetorkInterfaces
	'''
	class Meta:
		model = VTServer
		exclude = ('numberofCPUs', 'memory', 'CPUFrequency',
		'discSpaceGB', 'url', 'subscribedMacRanges', 'subscribedIp4Ranges')

	agentPassword = forms.CharField(label='Agent Password',widget=forms.PasswordInput())
