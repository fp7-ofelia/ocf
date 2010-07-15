'''
Created on Apr 29, 2010

@author: jnaous
'''
from django import forms
from expedient.clearinghouse.aggregate.models import Aggregate
from expedient.common.extendable.utils import get_subclasses_contenttype_qs
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

def _get_aggregate_types():
    agg_plugin_names = getattr(settings, "AGGREGATE_PLUGINS", [])
    l = []
    for n in agg_plugin_names:
        mod, sep, name = n.rpartition(".")
        mod = __import__(mod, fromlist=[name])
        l.append(ContentType.objects.get_for_model(getattr(mod, name)).id)
    return ContentType.objects.filter(id__in=l)

class ContentTypeChoiceField(forms.ModelChoiceField):
    """Create a label from the verbose name of the class"""
    def label_from_instance(self, obj):
        return "%s" % obj

class AggregateTypeForm(forms.Form):
    type = ContentTypeChoiceField(
        label="Aggregate Type",
        queryset=_get_aggregate_types(),
        widget=forms.Select(attrs={'style':"width: 300px;"}))
