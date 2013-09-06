'''
Created on Jan 14, 2013

@author: CarolinaFernandez
'''

from django import forms
from expedient.common.utils.validators import resourceVMNameValidator
from vt_plugin.models.VM import VM

class VMModelForm(forms.models.ModelForm):

    class Meta:
        fields=["disc_image", "name", "memory", "hdSetupType", "virtualizationSetupType"]
        model = VM

    def clean_name(self):
        resourceVMNameValidator(self.cleaned_data['name'])
        return self.cleaned_data['name']

