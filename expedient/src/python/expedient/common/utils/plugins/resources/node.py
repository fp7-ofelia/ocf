"""
Defines the fields for the nodes sent to the TopologyGenerator.

@date: Feb 20, 2013
@author: CarolinaFernandez
"""

class Node():

    def __init__(self, name, type, description, image, aggregate_id, available, location):
        self.name = name
        self.type = type
        self.description = description
        self.image = image
        self.aggregate = aggregate_id
        self.available = available
        self.location = location

