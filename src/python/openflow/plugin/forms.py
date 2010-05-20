'''
Created on Apr 29, 2010

@author: jnaous
'''

from django import forms
from models import OpenFlowAggregate

class OpenFlowAggregateForm(forms.ModelForm):
    '''
    A form to create and edit OpenFlow Aggregates.
    '''

    class Meta:
        model = OpenFlowAggregate
        exclude = ['client', 'admins_info', 'slices_info', 'projects_info',
                   'users_info']
