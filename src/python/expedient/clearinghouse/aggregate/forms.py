'''
Created on Apr 29, 2010

@author: jnaous
'''
from django import forms
from expedient.clearinghouse.aggregate.models import Aggregate
from expedient.common.extendable.utils import get_subclasses_verbose_names

def _get_aggregate_types():
    return get_subclasses_verbose_names(Aggregate)

class AggregateTypeForm(forms.Form):
    type = forms.ChoiceField(
        label="Aggregate Type",
        choices=_get_aggregate_types())
