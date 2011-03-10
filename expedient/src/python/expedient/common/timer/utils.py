'''Utilities and helper functions.
Created on Feb 16, 2011

@author: jnaous
'''

def stringify_func(f):
    if callable(f):
        return "%s.%s" % (f.__module__, f.__name__)
    else:
        return f
