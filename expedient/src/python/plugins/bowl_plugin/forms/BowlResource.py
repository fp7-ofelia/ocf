#
# BOWL expedient plugin for the Berlin Open Wireless Lab
# based on the sample plugin
#
# Authors: Theresa Enghardt (tenghardt@inet.tu-berlin.de)
#          Robin Kuck (rkuck@net.t-labs.tu-berlin.de)
#          Julius Schulz-Zander (julius@net.t-labs.tu-berlin.de)
#          Tobias Steinicke (tsteinicke@net.t-labs.tu-berlin.de)
#
# Copyright (C) 2013 TU Berlin (FG INET)
# All rights reserved.
#
'''
Created on Jul 08, 2013

@author: Theresa Enghardt
'''

from django import forms
from bowl_plugin.models.BowlResource import BowlResource as BowlResourceModel
#from sample_resource.utils.validators import validate_resource_name, validate_temperature_scale

class BowlResource(forms.models.ModelForm):

    connections = forms.ModelMultipleChoiceField(queryset = BowlResourceModel.objects.all().order_by("name"),
#                                                 widget = forms.SelectMultiple())
                                                 widget = forms.CheckboxSelectMultiple())

    class Meta:
        fields = ["name", "connections"]
        model = BowlResourceModel

    def __init__(self, *args, **kwargs):
        super(BowlResource, self).__init__(*args,**kwargs)
        try:
            # Do not allow links to self
            current_label = kwargs['instance'].label
            self.fields['connections'].queryset = BowlResourceModel.objects.exclude(label = current_label).order_by("name")
        except:
            pass

    def clean_name(self):
        #validate_resource_name(self.cleaned_data['name'])
        return self.cleaned_data['name']

#    def clean_temperature_scale(self):
#        validate_temperature_scale(self.cleaned_data['temperature_scale'])
#        return self.cleaned_data['temperature_scale']
#
