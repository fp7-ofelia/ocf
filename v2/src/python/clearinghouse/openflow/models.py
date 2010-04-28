'''
Created on Apr 26, 2010

@author: jnaous
'''

import os
from django.db import models
from clearinghouse.resources import models as resource_models
from clearinghouse.slice import models as slice_models
from clearinghouse.aggregate import models as aggregate_models
from clearinghouse.xmlrpc.models import PasswordXMLRPCClient
from django.core import serializers

class OpenFlowAdminInfo(aggregate_models.AggregateAdminInfo):
    pass

class OpenFlowUserInfo(aggregate_models.AggregateUserInfo):
    pass

class OpenFlowSliceInfo(aggregate_models.AggregateSliceInfo):
#    def get_rpc_info(self):
#        '''
#        Get the information about the slice to use in XML-RPC with AM.
#        
#        @return {'id': self.slice.id, 'name': self.slice.name,
#                 'description': self.slice.description}
#        '''
#        
#        for sw in self.slice.openflowswitchsliver_set.\
#        filter(switch__aggregate=self):
#        
#        
#        return {'id': self.slice.id, 'name': self.slice.name,
#                'description': self.slice.description}
#        
#    def get_switches_info(self):
#        '''
#        Get the information about switches in the topology to
#        use in XML-RPC with the AM. For each switch in the topology
#        of the aggregate, returns a dict that has the following keys.
#        
#        - C{dpid}: the switch's datapath id
#        - C{flowspace}: an array of dicts describing the switch's flowspace
#            Each such dict has the following keys:
#                - C{port}: the port for this flowspace
#                - C{direction}: 'ingress', 'egress', or 'bidirectional'
#                - C{policy}: 1 for 'allow', -1 for 'deny', 0 for read only
#                - C{dl_src}: link layer address in "xx:xx:xx:xx:xx:xx" format
#                    or '*' for wildcard
#                - C{dl_dst}: link layer address in "xx:xx:xx:xx:xx:xx" format
#                    or '*' for wildcard
#                - C{vlan_id}: vlan id as an int or -1 for wildcard
#                - C{nw_src}: network address in "x.x.x.x" format
#                    or '*' for wildcard
#                - C{nw_dst}: network address in "x.x.x.x" format
#                    or '*' for wildcard
#                - C{nw_proto}: network protocol as an int or -1 for wildcard
#                - C{tp_src}: transport port as an int or -1 for wildcard
#                - C{tp_dst}: transport port as an int or -1 for wildcard
#        
#        @return returns an array of dicts with information for each switch
#        '''
#        ret = []
#        for sw in self.slice.openflowswitchsliver_set.\
#        filter(switch__aggregate=self):
#            d = {'dpid': sw.switch.datapath_id}
#            fs_set = []
#            for fs in sw.flowspace_set.all():
#                fs_set = fs_set.append({
#                    'port': fs.interface.
#                })
    pass    

class OpenFlowProjectInfo(aggregate_models.AggregateProjectInfo):
    pass

class OpenFlowAggregate(aggregate_models.Aggregate):
    client = models.OneToOneField(PasswordXMLRPCClient)
    
    class Extend:
        replacements= {
            'admin_info_class': OpenFlowAdminInfo,
            'user_info_class': OpenFlowUserInfo,
            'slice_info_class': OpenFlowSliceInfo,
            'project_info_class': OpenFlowProjectInfo,
        }
        
    def update_slice(self, slice):
        slice.reserve_slice(slice)
        
    def reserve_slice(self, slice):
        # get all the slivers that are in this aggregate
        sw_slivers_qs = \
            slice.openflowswitchsliver_set.filter(switch__aggregate=self)
        link_slivers_qs = \
            slice.openflowswitchsliver_set.filter(switch__aggregate=self)
        
        sw_slivers_ser = serializers.serialize(
            'python', sw_slivers_qs,
            fields=(
                'resource',
                'flowspacerule_set',
            ),
            relations={
                'resource': {
                    'fields': (
                        'datapath_id',
                    ),
                },
                'flowspacerule_set': {
                    'excludes': (
                        'switch_sliver',
                    ),
                },
            },
        )
        
        sw_slivers = []
        for s in sw_slivers_ser:
            d = {}
            d['datapath_id'] = s['resource']['datapath_id']
            d['flowspace'] = []
            for fs in s['flowspacerule_set']:
                fsd = {}
                for f in ('direction', 'policy', 'dl_src', 'dl_dst', 'dl_type',
                'vlan_id', 'nw_src', 'nw_dst', 'nw_proto', 'tp_src', 'tp_dst',
                'port_num'):
                    fsd[f] = fs[f]
                d['flowspace'].append(fsd)
            sw_slivers.append(d)
            
        
        link_slivers_ser = serializers.serialize(
            'python', link_slivers_qs,
            fields=(
                'resource',
            ),
            relations={
                'resource': {
                    'fields': (
                        'link_id',
                    ),
                }  
            },
        )
        
        link_slivers = []
        for s in link_slivers_ser:
            d = {}
            d['link_id'] = s['resource']['link_id']
            link_slivers.append(d)
            
        return self.client.reserve_slice(
            slice.id, slice.project.name, slice.project.description,
            slice.name, slice.description,
            sw_slivers, link_slivers)
        
    def delete_slice(self, slice, server=None):
        return self.client.delete_slice(slice.id)

class OpenFlowSwitch(resource_models.Node):
    datapath_id = models.CharField(max_length=100, unique=True)
    
    class Extend:
        replacements={
            "sliver_class": "OpenFlowSwitchSliver",
        }

class OpenFlowLink(resource_models.Link):
    link_id = models.CharField(max_length=100)
    
    class Extend:
        replacements={
            "sliver_class": "OpenFlowLinkSliver",
            "nodes_through": "OpenFlowInterface",
            "node_class": OpenFlowSwitch,
        }

class OpenFlowInterface(models.Model):
    port_num = models.IntegerField()
    switch = models.ForeignKey(OpenFlowSwitch)
    link = models.ForeignKey(OpenFlowLink)

class OpenFlowSwitchSliver(resource_models.Sliver):
    class Extend:
        replacements={
            "resource_class": OpenFlowSwitch,
        }
    
class OpenFlowLinkSliver(resource_models.Sliver):
    class Extend:
        replacements={
            "resource_class": OpenFlowLink,
        }

class FlowSpaceRule(models.Model):
    TYPE_ALLOW = 1
    TYPE_DENY  = -1
    TYPE_RD_ONLY = 0
    
    POLICY_TYPE_CHOICES={TYPE_ALLOW: 'Allow',
                         TYPE_DENY: 'Deny',
                         TYPE_RD_ONLY: 'Read Only',
                         }
    
    DIR_IN = 'ingress'
    DIR_OUT = 'egress'
    DIR_BI = 'bidirectional'
    DIRECTION_CHOICES={DIR_IN: 'Ingress',
                       DIR_OUT: 'Egress',
                       DIR_BI: 'Bidirectional',
                       }

    direction = models.CharField(max_length=20,
                                 choices=DIRECTION_CHOICES.items(),
                                 default=DIR_BI)
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
    port_num = models.CharField(max_length=4, default="*")
    switch_sliver = models.ForeignKey(OpenFlowSwitchSliver)
    
    def __unicode__(self):
        return("Policy: "+FlowSpaceRule.POLICY_TYPE_CHOICES[self.policy]
               +", port: " +self.interface.port_num+", dl_src: "+self.dl_src
               +", dl_dst: "+self.dl_dst+", dl_type: "+self.dl_type
               +", vlan_id: "+self.vlan_id+", nw_src: "+self.nw_src
               +", nw_dst: "+self.nw_dst+", nw_proto: "+self.nw_proto
               +", tp_src: "+self.tp_src+", tp_dst: "+self.tp_dst)
