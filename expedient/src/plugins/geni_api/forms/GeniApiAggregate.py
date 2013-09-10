"""
Model for the GeniApi aggregate.
It defines the fields that will be used in the CRUD form.

@date: Apr 2, 2013
@author: CarolinaFernandez
"""

from django import forms
from geni_api.models import GeniApiAggregate as GeniApiAggregateModel

class GeniApiAggregate(forms.ModelForm):
    '''
    A form to create and edit GeniApi Aggregates.
    '''
    
   
    class Meta:
        model = GeniApiAggregateModel
        exclude = ['client', 'owner', 'users', 'available', 'username', 'password','url','api_version','rspec_version','urn','uuid']

    
