'''
Created on Oct 17, 2012

@author: lbergesio
'''

from openflow.plugin.models import OpenFlowInterfaceSliver, FlowSpaceRule,OpenFlowAggregate
from expedient.clearinghouse.geni.gopenflow.models import GCFOpenFlowAggregate
from django.db.models import Q

VLAN_TAG_SUBSET = 10

def calculate_free_vlan(slice):

    #aggs_filter = (Q(leaf_name=OpenFlowAggregate.__name__.lower()) |
    #               Q(leaf_name=GCFOpenFlowAggregate.__name__.lower()))
    #aggs_filter = ((Q(leaf_name=OpenFlowAggregate.__name__.lower()) & Q(available = True)) | 
    #                (Q(leaf_name=GCFOpenFlowAggregate.__name__.lower()) & Q(available = True)))

    #of_aggs = slice.aggregates.filter(aggs_filter)

    #Returns of ams only of the of ports and switches selected.
    of_aggs = list(set([x.resource.aggregate for x in OpenFlowInterfaceSliver.objects.filter(slice=slice)]))

    available_vlans = []
    free_vlan = None

    if len(of_aggs) == 1:
        #XXX pass parameter to get_offered_vlans to retrieve less vlans
        free_vlan =  of_aggs[0].as_leaf_class().get_offered_vlans(1)

    else:
        got_vlan = False
        subset = VLAN_TAG_SUBSET
        while(not got_vlan):
            for of_agg in of_aggs:
                available_vlans += of_agg.as_leaf_class().get_offered_vlans(subset)
            temp_vlans = {}
            for v in available_vlans:
                if temp_vlans[v] == len(of_agg):
                     free_vlan = v
                     got_vlan = True
                     break
                elif v not in temp_vlans:
                    temp_vlans[v]=0
                else:
                    temp_vlans[v]=temp_vlans[v]+1
            if subset >= 4096:
                raise Exception("There is no free vlan to slice your experiment in all the affected AMs. Plase switch no advanced mode, choose your flowspace and wait for the admins decision.")
            elif free_vlan == None:
                subset+=VLAN_TAG_SUBSET   
    return free_vlan

def create_simple_slice_vlan_based(vlan_tag, slice):
    #create a simple flowspacerule containing only the vlans tags and the OF ports
    newfsrule = FlowSpaceRule(vlan_id_start=vlan_tag, vlan_id_end=vlan_tag)
    newfsrule.save()
    #attached ports
    for ofsliver in OpenFlowInterfaceSliver.objects.filter(slice=slice).distinct():
        newfsrule.slivers.add(ofsliver)
    newfsrule.save()  

def check_existing_flowspace_in_slice(slice): 
    if FlowSpaceRule.objects.filter(slivers__slice=slice).distinct():
        return True
    return False
