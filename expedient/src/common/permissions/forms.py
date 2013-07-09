'''
Created on Jun 10, 2010

@author: jnaous
'''
from django import forms
from django.contrib.auth.models import User
from expedient.common.utils.validators import *
from models import PermissionRequest

class PermissionRequestForm(forms.ModelForm):
    """
    A form that can be used to request a permission from another user.

    """
    message = forms.CharField(required=True, widget=forms.Textarea, label="Description")

    class Meta:
        fields=["permission_owner", "message"] 
        model = PermissionRequest

    def __init__(self, permission_owners_qs, *args, **kwargs):
        """
        Set the permission_owners queryset.
        """
        super(PermissionRequestForm, self).__init__(*args, **kwargs)
        self.fields["permission_owner"].queryset = permission_owners_qs

class ProjectRequestForm(PermissionRequestForm):
    """
    A form that can be used to request a project creation.
    """
    # Permission owner (dropdown list) is available in the form but hidden, so this value can
    # be passed to the father Form (PermissionRequestForm) and processed then at the __init__
    permission_owner = forms.ModelChoiceField(required=False, queryset=User.objects.filter(is_superuser=1), help_text="User you want to ask permissions for", label="", widget=forms.HiddenInput)
    name = forms.CharField(required=True, help_text="Name of the project", validators=[asciiValidator])
    organization = forms.CharField(required=True, help_text="Name of your organization", validators=[asciiValidator])
    duration = forms.CharField(required=True, help_text="Approximate duration of the project", label="End date (approx)")

    class Meta:
        fields=["permission_owner", "name", "organization", "duration", "message"]
        model = PermissionRequest

    def clean_message(self):
        # Copy the contents of 'name', 'organization' and 'duration' inside the 'message'
        name = self.cleaned_data.get('name', None)
        duration = self.cleaned_data.get('duration', None)
        organization = self.cleaned_data.get('organization', None)
        message = self.cleaned_data.get('message', None)
        aux_message = ""
        if name:
            aux_message += "* Project name: " + name + " || "
        if organization:
            aux_message += "* Organization: " + organization + " || "
        if duration:
            aux_message += "* End date (approx): " + duration + " || "
        # Return the new forged message
        aux_message += "* Project description: " + message
        return aux_message

    def clean_permission_owner(self):
        superuser = User.objects.filter(is_superuser=1)[0]
        return superuser

    def clean(self):
        # Remove fields that are not in the Model to avoid any mismatch when synchronizing
        d = dict(self.cleaned_data)
        if "name" in d:
            del d["name"]
        if "organization" in d:
            del d["organization"]
        if "duration" in d:
            del d["duration"]
        p = self._meta.model(**d)
        return self.cleaned_data
