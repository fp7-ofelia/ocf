'''
Created on Apr 29, 2010

@author: jnaous
'''

from django import forms
from models import OpenFlowAggregate, OpenFlowSliceInfo, OpenFlowConnection

class OpenFlowAggregateForm(forms.ModelForm):
    '''
    A form to create and edit OpenFlow Aggregates.
    '''

    class Meta:
        model = OpenFlowAggregate
        exclude = ['client', 'owner', 'users']

class OpenFlowSliceInfoForm(forms.ModelForm):
    class Meta:
        model = OpenFlowSliceInfo
        exclude = ["slice"]

class OpenFlowStaticConnection(forms.ModelForm):
    def __init__(self, aggregate, *args, **kwargs):
        super(OpenFlowStaticConnection, self).__init__(*args, **kwargs)
        self.aggregate = aggregate
        
    class Meta:
        model = OpenFlowConnection
        