'''
Created on Apr 29, 2010

@author: jnaous
'''
from django import forms
from expedient.clearinghouse.aggregate.utils import get_aggregate_types

class ContentTypeChoiceField(forms.ModelChoiceField):
    """Create a label from the verbose name of the class"""
    def label_from_instance(self, obj):
        return "%s" % obj

class AggregateTypeForm(forms.Form):
    type = ContentTypeChoiceField(
        label="Aggregate Type",
        queryset=get_aggregate_types(),
        widget=forms.Select(attrs={'style':"width: 300px;"}))
