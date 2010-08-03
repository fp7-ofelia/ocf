'''
Created on Aug 2, 2010

@author: jnaous
'''
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

def get_aggregate_classes():
    """
    Get the list of modules that are the aggregate classes
    of aggregate plugins.
    """
    agg_plugin_names = getattr(settings, "AGGREGATE_PLUGINS", [])
    l = []
    for n in agg_plugin_names:
        mod, _, name = n.rpartition(".")
        mod = __import__(mod, fromlist=[name])
        print mod
        print name
        l.append(getattr(mod, name))
    return l

def get_aggregate_types():
    """
    Return the ContentType queryset of installed plugin aggregate models.
    """
    l = get_aggregate_classes()
    l = [ContentType.objects.get_for_model(m).id for m in l]
    return ContentType.objects.filter(id__in=l)
