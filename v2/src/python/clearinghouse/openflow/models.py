from django.db import models
from clearinghouse import aggregate
from clearinghouse import resources
from clearinghouse import slice

class Aggregate(aggregate.models.Aggregate):
    shared_key = models.CharField(max_length=1024)
    url = models.CharField(max_length=1024)
    
    class Extend:
        replacements= {
            'sliver_class': "OpenFlowSliver",
        }
    
    def create_slice(self, slice_id, *args, **kwargs):
        '''Create a new slice with the given slice_id
        and the resources specified. Does not actually
        make the reservation. Use start_slice for that.
        
        @param slice_id: unique id to give to the slice
        @type slice_id: L{str}
        @param args: additional optional arguments
        @param kwargs: additional optional keyword arguments
        '''
        raise NotImplementedError()
    
    def start_slice(self, slice_id, *args, **kwargs):
        '''Reserves/allocates the resources in the aggregate
        
        @param slice_id: unique id of slice to start
        @type slice_id: L{str}
        @param args: additional optional arguments
        @param kwargs: additional optional keyword arguments
        '''
        raise NotImplementedError()
    
    def delete_slice(self, slice_id, *args, **kwargs):
        '''Delete slice with given slice_id
        
        @param slice_id: unique id of slice to delete
        @type slice_id: L{str}
        @param args: additional optional arguments
        @param kwargs: additional optional keyword arguments
        '''
        raise NotImplementedError()
    
    def stop_slice(self, slice_id, *args, **kwargs):
        '''Stops running the slice, but does not delete it.
        
        @param slice_id: unique id of slice to stop
        @type slice_id: L{str}
        @param args: additional optional arguments
        @param kwargs: additional optional keyword arguments
        '''
        raise NotImplementedError()

class Switch(resources.models.Node):
    class Extend:
        replacements={
            "sliver_class": "SwitchSliver"
        }

class Link(resources.models.Link):
    class Extend:
        replacements={
            "sliver_class": "LinkSliver",
            "nodes_through": "Interface",
            "node_class": Switch,
        }

class FlowSpaceRule(models.Model):
    TYPE_ALLOW = 1
    TYPE_DENY  = -1
    TYPE_RD_ONLY = 0
    
    POLICY_TYPE_CHOICES={TYPE_ALLOW: 'Allow',
                         TYPE_DENY: 'Deny',
                         TYPE_RD_ONLY: 'Read Only',
                         }

    policy = models.SmallIntegerField(choices=POLICY_TYPE_CHOICES.items(),
                                      default=TYPE_ALLOW)
    dl_src = models.CharField(max_length=17, default="*")
    dl_dst = models.CharField(max_length=17, default="*")
    dl_type = models.CharField(max_length=5, default="*")
    vlan_id = models.CharField(max_length=4, default="*")
    nw_src = models.CharField(max_length=18, default="*")
    nw_dst = models.CharField(max_length=18, default="*")
    nw_proto = models.CharField(max_length=3, default="*")
    tp_src = models.CharField(max_length=5, default="*")
    tp_dst = models.CharField(max_length=5, default="*")
    interface = models.ForeignKey("Interface")
    switch_sliver = models.ForeignKey("SwitchSliver")
    
    def __unicode__(self):
        return("Policy: "+FlowSpaceRule.POLICY_TYPE_CHOICES[self.policy]
               +", port: " +self.interface.port_num+", dl_src: "+self.dl_src
               +", dl_dst: "+self.dl_dst+", dl_type: "+self.dl_type
               +", vlan_id: "+self.vlan_id+", nw_src: "+self.nw_src
               +", nw_dst: "+self.nw_dst+", nw_proto: "+self.nw_proto
               +", tp_src: "+self.tp_src+", tp_dst: "+self.tp_dst)
    
class Interface(models.Model):
    port_num = models.IntegerField()
    switch = models.ForeignKey(Switch)
    link = models.ForeignKey(Link)

class SwitchSliver(resources.models.Sliver):
    switch = models.ForeignKey(Switch)
    slice = models.ForeignKey(slice.models.Slice)
    
class LinkSliver(resources.models.Sliver):
    link = models.ForeignKey(Link)
    slice = models.ForeignKey(slice.models.Slice)

    