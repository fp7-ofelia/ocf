'''
Created on Jun 16, 2010

@author: jnaous
'''
from django.conf import settings

class RegexMatcher(object):
    """
    Reads a list of regular expressions from a setting and adds a method
    to match any of the regular expressions.
    """
    
    def __init__(self, setting_name):
        import re
        self.patterns = []
        for regex in getattr(settings, setting_name, ()):
            self.patterns.append(re.compile(regex))
        
    def matches(self, path):
        for p in self.patterns:
            m = p.match(path)
            if m:
                return m

