from django.db import models
from clearinghouse.aggregate.models import Aggregate

class Resource(models.Model):
    '''
    Abstract model of a resource.
    '''
    
    # @ivar aggregate: The aggregate that controls/owns this resource
    aggregate = models.ForeignKey(Aggregate)
    
    # @ivar name: A human-readable name for the resources
    name = models.CharField(max_length=200)
    
    # @ivar id: A unique id for the resource
    # TODO: check other fields
    id = models.CharField(max_length=200, unique=True)
    
    def __unicode__(self):
        return u"Resource: %s (id %s) belonging to aggregate %s." % (
                        self.name, self.id, self.aggregate)
    
