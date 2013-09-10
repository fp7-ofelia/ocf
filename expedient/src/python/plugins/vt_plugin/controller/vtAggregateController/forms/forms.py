'''
Created on Apr 29, 2010

@author: jnaous
'''

from django import forms
from vt_plugin.models import VtPlugin
from expedient.common.utils import create_or_update
from django.forms.models import ModelChoiceField
from vt_plugin.models import xmlrpcServerProxy

class VTAggregateForm(forms.ModelForm):
    '''
    A form to create and edit OpenFlow Aggregates.
    '''

    class Meta:
        model = VtPlugin
        #exclude = ['client', 'owner', 'users', "leaf_name"]
        exclude = ['client', 'owner', 'users', 'available']

class xmlrpcServerProxyForm(forms.ModelForm):
    '''
    A form to create and edit OpenFlow Aggregates.
    '''

    confirm_password = forms.CharField(
        help_text="Confirm password.",
        max_length=40,
        widget=forms.PasswordInput(render_value=False))

    def __init__(self, check_available=False, *args, **kwargs):
        super(xmlrpcServerProxyForm, self).__init__(*args, **kwargs)
        self.check_available = check_available
        # Fix Django's autocompletion of username/password fields when type is password
        self.fields['username'].widget.attrs["autocomplete"] = 'off'
        self.fields['password'].widget.attrs["autocomplete"] = 'off'
        self.fields['confirm_password'].widget.attrs["autocomplete"] = 'off'

    class Meta:
        model = xmlrpcServerProxy
        # Defines all the fields in the model by ORDER
        fields = ('username', 'password', 'confirm_password', 'url')
        # Form widgets: HTML representation of fields
        widgets = {
            # Shows the password
            'password': forms.PasswordInput(render_value=True),
        }

    # Validation and so on
    def clean(self):
        # Check that both passwords (if present) are the same
        password = self.cleaned_data.get('password', None)
        confirm_password = self.cleaned_data.get('confirm_password', None)
        if password and confirm_password and (password != confirm_password):
            raise forms.ValidationError("Passwords don't match")
        # Remove fields that are not in the Model to avoid any mismatch when synchronizing
        d = dict(self.cleaned_data)
        if "confirm_password" in d:
            del d["confirm_password"]
        p = self._meta.model(**d)
        return self.cleaned_data

