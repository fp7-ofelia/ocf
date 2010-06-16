'''
Created on Jun 12, 2010

@author: jnaous
'''
from django import forms
from expedient.clearinghouse.aggregate.tests.models import DummyAggregate

class DummyAggForm(forms.ModelForm):
    class Meta:
        model = DummyAggregate
        exclude = ['admins_info', 'slices_info', 'projects_info', 'users_info']
