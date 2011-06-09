'''
Created on Apr 29, 2010

@author: jnaous
'''

from inheritance import itersubclasses
from django.contrib.contenttypes.models import ContentType

def get_subclasses_verbose_names(cls):
    for subcls in itersubclasses(cls):
        yield ("%s.%s" % (subcls.__module__, subcls.__name__),
               subcls._meta.verbose_name)

def get_subclasses_contenttype_qs(cls):
    ids = [ContentType.objects.get_for_model(subcls).id \
           for subcls in itersubclasses(cls)]
    return ContentType.objects.filter(id__in=ids)
