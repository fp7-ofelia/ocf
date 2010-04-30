'''
Created on Apr 26, 2010

@author: jnaous
'''

from django.db import models
from clearinghouse.resources import models as resource_models
from clearinghouse.aggregate import models as aggregate_models
from clearinghouse.xmlrpc.models import PasswordXMLRPCClient
from django.core.urlresolvers import reverse

class OpenFlowAdminInfo(aggregate_models.AggregateAdminInfo):
    pass

class OpenFlowUserInfo(aggregate_models.AggregateUserInfo):
    pass

class OpenFlowSliceInfo(aggregate_models.AggregateSliceInfo):
    controller_url = models.CharField("URL of the slice's OpenFlow controller",
                                      max_length=100)

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
        
    class Meta:
        verbose_name = "OpenFlow Aggregate"

    def update_slice(self, slice):
        slice.reserve_slice(slice)
        
    def create_slice(self, user, slice, slice_password):
        # get all the slivers that are in this aggregate
        sw_slivers_qs = \
            slice.openflowswitchsliver_set.filter(switch__aggregate=self)
        sw_slivers_qs.select_related('resource', 'flowspacerule_set')
        
        sw_slivers = []
        for s in sw_slivers_qs:
            d = {}
            d['datapath_id'] = s.resource.datapath_id
            d['flowspace'] = []
            for fs in s.flowspacerule_set:
                fsd = {}
                for f in fs._meta.fields:
                    fsd[f.name] = getattr(fs, f.name)
                d['flowspace'].append(fsd)
            sw_slivers.append(d)
        
        return self.client.reserve_slice(
            slice.id, slice.project.name, slice.project.description,
            slice.name, slice.description, 
            slice.openflowsliceinfo.controller_url,
            user.email, slice_password, sw_slivers)
        
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

    switch_sliver = models.ForeignKey(OpenFlowSwitchSliver)

    direction = models.CharField(max_length=20,
                                 choices=DIRECTION_CHOICES.items(),
                                 default=DIR_BI)
    policy = models.SmallIntegerField(choices=POLICY_TYPE_CHOICES.items(),
                                      default=TYPE_ALLOW)
    dl_src_start = models.CharField('Link layer source address range start',
                                    max_length=17, default="*")
    dl_dst_start = models.CharField('Link layer destination address range start',
                                    max_length=17, default="*")
    dl_type_start = models.CharField('Link layer type range start',
                                     max_length=5, default="*")
    vlan_id_start = models.CharField('VLAN ID range start',
                                     max_length=4, default="*")
    nw_src_start = models.CharField('Network source address range start',
                                    max_length=18, default="*")
    nw_dst_start = models.CharField('Network destination address range start',
                                    max_length=18, default="*")
    nw_proto_start = models.CharField('Network protocol range start',
                                      max_length=3, default="*")
    tp_src_start = models.CharField('Transport source port range start',
                                    max_length=5, default="*")
    tp_dst_start = models.CharField('Transport destination port range start',
                                    max_length=5, default="*")
    port_num_start = models.CharField('Switch port number range start',
                                      max_length=4, default="*")
    
    dl_src_end = models.CharField('Link Layer Source Address Range End',
                                  max_length=17, default="*")
    dl_src_end = models.CharField('Link layer source address range end',
                                    max_length=17, default="*")
    dl_dst_end = models.CharField('Link layer destination address range end',
                                    max_length=17, default="*")
    dl_type_end = models.CharField('Link layer type range end',
                                     max_length=5, default="*")
    vlan_id_end = models.CharField('VLAN ID range end',
                                     max_length=4, default="*")
    nw_src_end = models.CharField('Network source address range end',
                                    max_length=18, default="*")
    nw_dst_end = models.CharField('Network destination address range end',
                                    max_length=18, default="*")
    nw_proto_end = models.CharField('Network protocol range end',
                                      max_length=3, default="*")
    tp_src_end = models.CharField('Transport source port range end',
                                    max_length=5, default="*")
    tp_dst_end = models.CharField('Transport destination port range end',
                                    max_length=5, default="*")
    port_num_end = models.CharField('Switch port number range end',
                                      max_length=4, default="*")
    
    def __unicode__(self):
        return("Policy: "+FlowSpaceRule.POLICY_TYPE_CHOICES[self.policy]
               +", port: " +self.interface.port_num+", dl_src: "+self.dl_src
               +", dl_dst: "+self.dl_dst+", dl_type: "+self.dl_type
               +", vlan_id: "+self.vlan_id+", nw_src: "+self.nw_src
               +", nw_dst: "+self.nw_dst+", nw_proto: "+self.nw_proto
               +", tp_src: "+self.tp_src+", tp_dst: "+self.tp_dst)
