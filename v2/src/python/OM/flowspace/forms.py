# forms to be used with flowspace app
from django import forms
from OM.flowspace.models import OptedInFlowSpace, AdminFlowSpace, RequestedAdminFlowSpace, RequestedUserFlowSpace

class OptedInFlowSpaceForm(forms.ModelForm):
    class Meta:
        model = OptedInFlowSpace
        exclude = ('user',)