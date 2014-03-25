from openflow.plugin.models import OpenFlowInterfaceSliver
import random

class VlanManager:

    """
    Class designed to retrieve a VLAN avaialable between one or more OFAMs.
    This class is meant to be extended to support locks, handle multi-concurrency 
    and use improved algorithms to get the final available VLAN.
    """
    
    def __init__(self, input_list=list()):
        self.input_buffer = input_list
        self.current_intersection = set(range(0,4096))

    def process(self,expedient_slice,vlan_range_len=1):
        """
        Main method
        """
        aggs = self.get_slice_ams(expedient_slice)
        if len(aggs)==1 and vlan_range_len==1:
            return self.retrieve_one_random_vlan(aggs[0],vlan_range_len)
        used_vlans = self.get_all_used_vlans(aggs)
        available_vlans = self.convert_all_used_to_available_vlans(used_vlans)
        self.add_input(available_vlans)
        return self.get_result(vlan_range_len)

    """
    AM Management Functions
    """

    def get_slice_ams(self, expedient_slice):
        return list(set([x.resource.aggregate for x in OpenFlowInterfaceSliver.objects.filter(slice=expedient_slice)]))
   
    def get_single_am_vlan_set(self, ofam):
        return ofam.as_leaf_class().get_used_vlans() 

    def get_all_used_vlans(self, all_ofams):
        used_vlans = list()
        for ofam in all_ofams:
            used_vlan_set = self.get_single_am_vlan_set(ofam)
            used_vlans.append(used_vlan_set)
        return used_vlans
    
    def retrieve_one_random_vlan(self, ofam, vlan_range_len):
        return ofam.as_leaf_class().get_used_vlans(direct_output=True)
 
    """
    VLAN Sets Operations
    """

    def get_intersection(self, setA, setB):
        return setA & setB

    def get_result(self, vlan_range_len):
        self.intersect()
        if vlan_range_len > 1:
            return self.get_final_available_vlan_range(vlan_range_len)
        else:
            return self.get_final_available_vlan()

    def get_final_available_vlan(self):
        rand = random.randrange(0, len(self.current_intersection))
        return list(self.current_intersection)[rand]
    
    def get_final_available_vlan_range(self, vlan_range_len):
        intersection=list(self.current_intersection)
        rand = random.randrange(0, (len(intersection) - vlan_range_len))
        if intersection[rand] == (intersection[rand + vlan_range_len] - vlan_range_len):
            return intersection[rand:(rand + vlan_range_len)]
        else:
            self.get_final_available_vlan_range(vlan_range_len)      

    def intersect(self):
        intersection = self.current_intersection
        for vlan_set in self.input_buffer:
            intersection = self.get_intersection(intersection, self.convert_to_set(vlan_set))
            if not intersection:
                self.clear_input_buffer()
                raise Exception("No available VLAN found")
        self.clear_input_buffer()
        self.current_intersection = intersection

    """
    Utils
    """

    def add_input(self, in_set):
        if isinstance(in_set[0], list):
            self.input_buffer.extend(in_set)
        else:
            self.input_buffer.append(in_set)

    def clear_input_buffer(self):
        self.input_buffer = list()

    def reset_current_intersection(self):
        self.current_intersection = set(range(0,4096))

    def reset(self):
        self.clear_input_buffer()
        self.reset_current_intersection()
    
    def convert_to_set(self, vlan_set):
        if isinstance(vlan_set, set):
            return vlan_set
        else:
            return set(vlan_set)   
    
    def convert_all_used_to_available_vlans(self, used_vlans):
        available_vlans = list()
        for used_vlan_set in used_vlans:
            available_vlans.append(self.convert_used_to_available_vlans(used_vlan_set))
        return available_vlans
    
    def convert_used_to_available_vlans(self, collection):
        return list(set(range(0,4096)) - set(collection))
