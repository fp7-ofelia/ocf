'''
@author: jnaous
'''
from django.db import models
from expedient.clearinghouse.aggregate.models import Aggregate
from expedient.common.extendable.models import Extendable
from expedient.clearinghouse.slice.models import Slice
from expedient.common.permissions.models import ControlledModel

class Resource(Extendable, ControlledModel):
    '''
    Generic model of a resource.
    
    @param aggregate: The L{Aggregate} that controls/owns this resource
    @type aggregate: L{models.ForeignKey} to L{Aggregate}
    @param name: A human-readable name for the resource
    @type name: L{str}
    '''
    
    name = models.CharField(max_length=200)
    available = models.BooleanField("Available", default=True, editable=False)
    status_change_timestamp = models.DateTimeField(editable=False)
    aggregate = models.ForeignKey(
        Aggregate, verbose_name="Aggregate the resource belongs to")
    slice_set = models.ManyToManyField(
        Slice, through="Sliver", verbose_name="Slices this resource is used in")
    
    def __unicode__(self):
        return u"Resource: %s belonging to aggregate %s." % (
            self.name, self.aggregate)

class Sliver(Extendable, ControlledModel):
    '''
    Information on the reservation of a particular resource for a slice.
    '''
    
    resource = models.ForeignKey(
        Resource, verbose_name="Resource this sliver is part of")
    slice = models.ForeignKey(
        Slice, verbose_name="Slice this sliver is part of")

class SliverSet(Extendable, ControlledModel):
    '''
    Groups Slivers.
    '''
    sliver_set = models.ManyToManyField(Sliver)

class AggregateSliverSet(SliverSet):
    """
    Groups slivers by Aggregate and Slice, and is used to work with
    slivers at an aggregate.
    """
    aggregate = models.ForeignKey(Aggregate)
    slice = models.ForeignKey(Slice)
