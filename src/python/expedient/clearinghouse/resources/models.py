'''
@author: jnaous
'''
from django.db import models
from expedient.clearinghouse.aggregate.models import Aggregate
from expedient.common.extendable.models import Extendable
from expedient.clearinghouse.slice.models import Slice

class Resource(Extendable):
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

#    class Extend:
#        fields = {
#            'aggregate': (
#                models.ForeignKey,
#                (Aggregate,),
#                {"verbose_name": "Aggregate the resource belongs to"},
#                ("aggregate_class",),
#                {"verbose_name":  "aggregate_comment"},
#            ),
#            'slices': (
#                models.ManyToManyField,
#                (Slice,),
#                {'through': "Sliver",
#                 'verbose_name': "Slices this resource is used in"},
#                (None,),
#                {'through': "sliver_class",
#                 'verbose_name': "slices_comment"},
#            ),
#        }
#        mandatory = ["aggregate_class", "sliver_class"]
    
    def __unicode__(self):
        if hasattr(self, "aggregate"):
            return u"Resource: %s belonging to aggregate %s." % (
                self.name, self.aggregate)
        else:
            return u"Resource: %s" % self.name

class Sliver(Extendable):
    '''
    Information on the reservation of a particular resource for a slice.
    '''
    
    resource = models.ForeignKey(
        Resource, verbose_name="Resource this sliver is part of")
    slice = models.ForeignKey(
        Slice, verbose_name="Slice this sliver is part of")
    
#    class Extend:
#        fields = {
#            'resource': (
#                models.ForeignKey,
#                (Resource,),
#                {"verbose_name": "Resource this sliver is part of"},
#                ("resource_class",),
#                {"verbose_name": "resource_comment"},
#            ),
#            'slice': (
#                models.ForeignKey,
#                (Slice,),
#                {"verbose_name": "Slice this sliver is part of"},
#                (None,),
#                {"verbose_name": "slice_comment"},
#            ),
#        }
