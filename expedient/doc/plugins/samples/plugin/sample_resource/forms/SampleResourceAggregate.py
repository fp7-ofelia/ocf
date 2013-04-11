'''
Created on Apr 2, 2013

@author: CarolinaFernandez
'''

from django import forms
from sample_resource.models import SampleResourceAggregate as SampleResourceAggregateModel

class SampleResourceAggregate(forms.ModelForm):
    '''
    A form to create and edit SampleResource Aggregates.
    '''

    sync_resources = forms.BooleanField(label = "Sync resources?", initial = True, required = False)

    class Meta:
        model = SampleResourceAggregateModel
        exclude = ['client', 'owner', 'users', 'available']

