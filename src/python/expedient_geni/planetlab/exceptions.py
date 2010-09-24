'''
Created on Jul 10, 2010

@author: jnaous
'''

class NameConflictException(Exception):
    """
    Raised when the same name is found in two different aggregates.
    """
    pass

class RSpecParsingException(Exception):
    """
    Raised when there is a problem parsing the RSpec.
    """
    pass