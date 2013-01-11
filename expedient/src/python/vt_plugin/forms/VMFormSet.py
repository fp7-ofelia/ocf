'''
Created on Jan 11, 2013

@author: CarolinaFernandez
'''

from django import forms
from expedient.common.utils.validators import resourceNameValidator
from vt_plugin.models.VM import VM

class VMFormSet(forms.models.BaseModelFormSet):

    class Meta:
        fields=["name", "memory","disc_image", "hdSetupType", "virtualizationSetupType"]
        model = VM

    def __init__(self, post, *args, **kwargs):
        super(VMFormSet, self).__init__(post, *args, **kwargs)
        if kwargs['queryset']:
            self.queryset = kwargs['queryset']

    def clean(self):
        name = self.forms[0].cleaned_data['name']
        resourceNameValidator(name)
        return self.cleaned_data

