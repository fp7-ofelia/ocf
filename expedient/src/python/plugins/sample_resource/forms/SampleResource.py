'''
Created on Jan 14, 2013

@author: CarolinaFernandez
'''

from django import forms
from sample_resource.utils.validators import validate_resource_name
from sample_resource.models.SampleResource import SampleResource

class SampleResourceModelForm(forms.models.ModelForm):

    class Meta:
        fields=["name", "temperature_scale", "interfaces"]
        model = SampleResource

    def clean_name(self):
        validate_resource_name(self.cleaned_data['name'])
        return self.cleaned_data['name']

