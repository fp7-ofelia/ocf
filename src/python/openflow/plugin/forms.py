'''
Created on Apr 29, 2010

@author: jnaous
'''

from django import forms
from models import OpenFlowAggregate, OpenFlowSliceInfo

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
