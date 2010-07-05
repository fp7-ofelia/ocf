'''
Created on Jul 4, 2010

@author: jnaous
'''

from django.db import models
from expedient.clearinghouse.aggregate.models import Aggregate

class GENIAggregateSliceInfo(models.Model):
    slice_urn = 

class GENIAggergate(Aggregate):
    url = models.URLField(max_length=200)
    
    def to_rspec(self, slice):
        """
        Change this slice into an rspec for this aggregates
        """
        raise NotImplementedError()
    
    def update(self, rspec):
        """
        Parse the rspec and update resources.
        """
        raise NotImplementedError()
    
