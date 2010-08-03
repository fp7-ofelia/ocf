'''
Created on Aug 2, 2010

@author: jnaous
'''
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

def get_aggregate_types():
    """
    Return the ContentType queryset of installed plugin aggregate models.
    """
    agg_plugin_names = getattr(settings, "AGGREGATE_PLUGINS", [])
    l = []
    for n in agg_plugin_names:
        mod, _, name = n.rpartition(".")
        mod = __import__(mod, fromlist=[name])
        l.append(ContentType.objects.get_for_model(getattr(mod, name)).id)
    return ContentType.objects.filter(id__in=l)
