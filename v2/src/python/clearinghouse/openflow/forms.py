'''
Created on Apr 29, 2010

@author: jnaous
'''

from django import forms
from clearinghouse.openflow.models import OpenFlowAggregate

class OpenFlowAggregateForm(forms.ModelForm):
    '''
    A form to create and edit OpenFlow Aggregates.
    '''

    class Meta:
        model = OpenFlowAggregate
        exclude = ['client']
