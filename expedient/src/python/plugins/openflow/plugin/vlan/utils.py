from openflow.plugin.models import OpenFlowInterfaceSliver 
from openflow.plugin.models import FlowSpaceRule

def create_slice_with_vlan_range(slice, vlan_range):
    if not isinstance(vlan_range,list):
         vlan_range = [vlan_range]
    #create a simple flowspacerule containing only the vlans tags and the OF ports
    newfsrule = FlowSpaceRule(vlan_id_start=vlan_range[0], vlan_id_end=vlan_range[-1])
    newfsrule.save()
    #attached ports
    for ofsliver in OpenFlowInterfaceSliver.objects.filter(slice=slice).distinct():
        newfsrule.slivers.add(ofsliver)
    newfsrule.save()


