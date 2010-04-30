'''
Created on Apr 29, 2010

@author: jnaous
'''
from django import forms
from clearinghouse.aggregate.models import Aggregate
from clearinghouse.extendable.utils import get_subclasses_verbose_names

def _get_aggregate_types():
    return get_subclasses_verbose_names(Aggregate)

class AggregateTypeForm(forms.Form):
    print "agg types**********: %s" % list(_get_aggregate_types())
    type = forms.ChoiceField(
        label="Aggregate Type",
        choices=_get_aggregate_types())
