'''
Created on Apr 21, 2010

@author: jnaous
'''

from django.db import models
from clearinghouse.resources import models as resource_models
from clearinghouse.slice import models as slice_models

class OpenFlowSwitch(resource_models.Node):
    datapath_id = models.CharField(max_length=100, unique=True)
    
    class Extend:
        replacements={
            "sliver_class": "OpenFlowSwitchSliver"
        }

class OpenFlowLink(resource_models.Link):
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
    interface = models.ForeignKey(OpenFlowInterface)
    switch_sliver = models.ForeignKey(OpenFlowSwitchSliver)
    
    def __unicode__(self):
        return("Policy: "+FlowSpaceRule.POLICY_TYPE_CHOICES[self.policy]
               +", port: " +self.interface.port_num+", dl_src: "+self.dl_src
               +", dl_dst: "+self.dl_dst+", dl_type: "+self.dl_type
               +", vlan_id: "+self.vlan_id+", nw_src: "+self.nw_src
               +", nw_dst: "+self.nw_dst+", nw_proto: "+self.nw_proto
               +", tp_src: "+self.tp_src+", tp_dst: "+self.tp_dst)
    
    def to_dict(self):
        pass
