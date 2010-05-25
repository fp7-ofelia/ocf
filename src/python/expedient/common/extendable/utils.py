'''
Created on Apr 29, 2010

@author: jnaous
'''

from inheritance import itersubclasses

def get_subclasses_verbose_names(cls):
    for subcls in itersubclasses(cls):
        yield ("%s.%s" % (subcls.__module__, subcls.__name__),
               subcls._meta.verbose_name)
