"""
Defines the fields for the nodes sent to the TopologyGenerator.

@date: Feb 20, 2013
@author: CarolinaFernandez
"""

class Node(object):

    def __init__(self, name, value, description, type, image, aggregate, **kwargs):
        # Adds news keys as attributes
        self.__dict__.update(kwargs)
        # Removes older kwarg's
        [ self.__dict__.pop(kwarg) if kwarg not in kwargs else kwarg for kwarg in self.__dict__ ]

        # May replace some values (e.g. 'aggregate')
        self.name = name
        self.value = value
        self.description = description
        self.type = type
        self.image = image
        self.aggregate = aggregate.pk
        self.available = aggregate.available
        self.location = aggregate.location

