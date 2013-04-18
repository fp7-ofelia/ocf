"""
Defines the fields for the links sent to the TopologyGenerator.

@date: Feb 20, 2013
@author: CarolinaFernandez
"""

class Link(object):

    def __init__(self, source, target, value, **kwargs):
        # Adds news keys as attributes
        self.__dict__.update(kwargs)
        # Removes older kwarg's
        [ self.__dict__.pop(kwarg) if kwarg not in kwargs else kwarg for kwarg in self.__dict__ ]

        # May replace some values (e.g. 'aggregate')
        self.source = source
        self.target = target
        self.value = value

