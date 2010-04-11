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
                (Slice, "Slices this resource is used in"),
                {'through': "Sliver"},
                (None, "slices_comment"),
                {'through': "sliver_class"},
            ),
        }
        mandatory = ["sliver_class"]
    
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
                (None, "resource_comment"),
                {},
            ),
            'slice': (
                models.ForeignKey,
                (Resource, "Slice this sliver is part of"),
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
                ("self", "Node's neighbors"),
                {'symmetrical': False},
                (None, "nodes_comment"),
                {'through': "neighbors_through"},
            )
        }
        redelegate = ['aggregate']
    
class Link(Resource):
    '''
    Links connect neighboring nodes.
    '''
    
    class Extend:
        fields = {
            'nodes': (
                models.ManyToManyField,
                ("self", "Nodes connected to this link"),
                {'related_name': 'links'},
                (None, "nodes_comment"),
                {'through': "nodes_through"},
            )
        }
        redelegate = ['aggregate']
