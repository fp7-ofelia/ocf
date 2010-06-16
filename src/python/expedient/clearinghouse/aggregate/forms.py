'''
Created on Apr 29, 2010

@author: jnaous
'''
from django import forms
from expedient.clearinghouse.aggregate.models import Aggregate
from expedient.common.extendable.utils import get_subclasses_contenttype_qs

def _get_aggregate_types():
    return get_subclasses_contenttype_qs(Aggregate)

class ContentTypeChoiceField(forms.ModelChoiceField):
    """Create a label from the verbose name of the class"""
    def label_from_instance(self, obj):
        return obj.model_class()._meta.verbose_name

class AggregateTypeForm(forms.Form):
    type = ContentTypeChoiceField(
        label="Aggregate Type",
        queryset=_get_aggregate_types(),
        widget=forms.Select(attrs={'style':"width: 300px;"}))
