# forms to be used with flowspace app
from django import forms
from optin_manager.flowspace.models import OptedInFlowSpace, AdminFlowSpace, RequestedAdminFlowSpace, RequestedUserFlowSpace

class OptedInFlowSpaceForm(forms.ModelForm):
    class Meta:
        model = OptedInFlowSpace
        exclude = ('user',)