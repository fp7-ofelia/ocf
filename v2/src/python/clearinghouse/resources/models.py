from django.db import models
from clearinghouse.aggregate.models import Aggregate
from clearinghouse.extendable.models import Extendable
from clearinghouse.slice.models import Slice

class Resource(Extendable):
    '''
    Generic model of a resource.
    
    @param aggregate: The L{Aggregate} that controls/owns this resource
    @type aggregate: L{models.ForeignKey} to L{Aggregate}
    @param name: A human-readable name for the resource
    @type name: L{str}
    '''
    
    name = models.CharField(max_length=200)
    
    class Extend:
        fields = {
            'aggregate': (
                models.ForeignKey,
                (Aggregate, "Aggregate the resource belongs to"),
                {},
                ("aggregate_class", "aggregate_comment"),
                {},
            ),
            'slices': (
                models.ManyToManyField,
                (Slice,),
                {'through': "Sliver",
                 'verbose_name': "Slices this resource is used in"},
                (None,),
                {'through': "sliver_class",
                 'verbose_name': "slices_comment"},
            ),
        }
        mandatory = ["aggregate_class", "sliver_class"]
    
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
    
    class Extend:
        fields = {
            'resource': (
                models.ForeignKey,
                (Resource, "Resource this sliver is part of"),
                {},
                ("resource_class", "resource_comment"),
                {},
            ),
            'slice': (
                models.ForeignKey,
                (Slice, "Slice this sliver is part of"),
                {},
                (None, "slice_comment"),
                {},
            ),
        }

class Node(Resource):
    '''
    Generic representation of a node
    
    @param neighbors: (optional) this node's neighbors
    @type neighbors: L{ManyToManyField} with "self"
    '''
    
    class Extend:
        fields = {
            'neighbors': (
                models.ManyToManyField,
                ("self",),
                {'symmetrical': False,
                 "verbose_name": "Node's neighbors"},
                (None,),
                {'through': "neighbors_through",
                 "verbose_name": "nodes_comment"},
            )
        }
        redelegate = ['aggregate', 'slices']
    
class Link(Resource):
    '''
    Links connect neighboring nodes.
    '''
    
    class Extend:
        fields = {
            'nodes': (
                models.ManyToManyField,
                (Node,),
                {'related_name': 'links',
                 'verbose_name': "Nodes connected to this link"},
                ("node_class",),
                {'through': "nodes_through",
                 'verbose_name': "nodes_comment"},
            )
        }
        redelegate = ['aggregate', 'slices']
