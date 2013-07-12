'''
Created on Jun 12, 2010

@author: jnaous
'''
from django import forms
from modules.aggregate.tests.models import DummyAggregate

class DummyAggForm(forms.ModelForm):
    class Meta:
        model = DummyAggregate
        fields = ["name", "description", "location", "available"]
