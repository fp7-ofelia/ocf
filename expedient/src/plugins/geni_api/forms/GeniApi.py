'''
Created on Jan 14, 2013

@author: CarolinaFernandez
'''

from django import forms
from geni_api.models.GeniApi import GeniApi as GeniApiModel
from geni_api.utils.validators import validate_resource_name, validate_temperature_scale

class GeniApi(forms.models.ModelForm):

    connections = forms.ModelMultipleChoiceField(queryset = GeniApiModel.objects.all().order_by("name"),
#                                                 widget = forms.SelectMultiple())
                                                 widget = forms.CheckboxSelectMultiple())

    class Meta:
        fields = ["name", "temperature_scale", "connections"]
        model = GeniApiModel

    def __init__(self, *args, **kwargs):
        super(GeniApi, self).__init__(*args,**kwargs)
        try:
            # Do not allow links to self
            current_label = kwargs['instance'].label
            self.fields['connections'].queryset = GeniApiModel.objects.exclude(label = current_label).order_by("name")
        except:
            pass

    def clean_name(self):
        validate_resource_name(self.cleaned_data['name'])
        return self.cleaned_data['name']

    def clean_temperature_scale(self):
        validate_temperature_scale(self.cleaned_data['temperature_scale'])
        return self.cleaned_data['temperature_scale']

