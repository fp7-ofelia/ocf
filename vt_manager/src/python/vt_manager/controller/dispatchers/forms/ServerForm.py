from vt_manager.models.VTServer import VTServer
from django import forms
from vt_manager.utils.EthernetUtils import EthernetUtils

class ServerForm(forms.ModelForm):
<<<<<<< HEAD
	'''
	A form for editing NetorkInterfaces
	'''
	class Meta:
		model = VTServer
		exclude = ('numberofCPUs', 'memory', 'CPUFrequency',
		'discSpaceGB', 'url', 'subscribedMacRanges', 'subscribedIp4Ranges')

	agentPassword = forms.CharField(label='Agent Password',widget=forms.PasswordInput(), help_text='Password set for the XMLRPC interface during the agent\'s installation')
=======
    ''' 
    A form for editing NetorkInterfaces
    '''

    agentPassword = forms.CharField(label='Agent Password', widget=forms.PasswordInput(render_value = True), help_text='Password set for the XMLRPC interface during the agent\'s installation')
    agentPasswordConfirm = forms.CharField(label='Confirm Agent Password', widget=forms.PasswordInput(render_value = False))

    # Form widgets: HTML representation of fields
    class Meta:
        model = VTServer
        exclude = ('numberofCPUs', 'memory', 'CPUFrequency',
            'discSpaceGB', 'url', 'subscribedMacRanges', 'subscribedIp4Ranges')

    # Validation and so on
    def clean(self):
        # Check that both passwords (if present) are the same
        password = self.cleaned_data.get('agentPassword', None)
        confirm_password = self.cleaned_data.get('agentPasswordConfirm', None)
        if password and confirm_password and (password != confirm_password):
            raise forms.ValidationError("Passwords don't match")
        # Remove fields that are not in the Model to avoid any mismatch when synchronizing
        d = dict(self.cleaned_data)
        if "agentPasswordConfirm" in d:
            del d["agentPasswordConfirm"]
        p = self._meta.model(**d)
        return self.cleaned_data
>>>>>>> 8973dbcd3e450399738a5324ba6d9057bc126156
