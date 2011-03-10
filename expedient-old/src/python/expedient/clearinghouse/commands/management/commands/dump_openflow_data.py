'''
Created on Oct 7, 2010

@author: jnaous
'''

from django.core.management.base import NoArgsCommand
from expedient.clearinghouse.project.models import Project
from expedient.ui.html.models import SliceFlowSpace
try:
    from json import dumps
except ImportError:
    from simplejson import dumps
    
from openflow.plugin.models import OpenFlowAggregate, OpenFlowSliceInfo

class Command(NoArgsCommand):
    help = "Dump serialized data for re-use in database migration."

    def handle_noargs(self, **options):
        
        # get the wanted data
        projects = []
        for obj in Project.objects.all():
            d = {"slices": []}
            for attr in "name", "description":
                d[attr] = getattr(obj, attr)
            
            for slice in obj.slice_set.all():
                s = {"ifaces": [], "sfs": []}
                
                for attr in "name", "description":
                    s[attr] = getattr(slice, attr)
                    
                info = OpenFlowSliceInfo.objects.get(slice=slice)
                for attr in "controller_url", "password":
                    s[attr] = getattr(info, attr)
                    
                for sliver in slice.sliver_set.all():
                    port = sliver.resource.as_leaf_class().port_num
                    dpid = sliver.resource.as_leaf_class().switch.datapath_id
                    s["ifaces"].append((dpid, port))
                    
                for sfs in SliceFlowSpace.objects.filter(slice=slice):
                    sfs_dict = {}
                    for attr in "dl_src", "dl_dst", "dl_type", "vlan_id", \
                    "nw_src", "nw_dst", "nw_proto", "tp_dst", "tp_src":
                        sfs_dict[attr] = getattr(sfs, attr)
                    s["sfs"].append(sfs_dict)
                
                d["slices"].append(s)
                
            projects.append(d)
            
        aggregates = []
        for agg in OpenFlowAggregate.objects.all():
            agg_dict = {}
            for attr in "name", "usage_agreement", "description", "location":
                agg_dict[attr] = getattr(agg, attr)
            
            for attr in "url", "username", "password":
                agg_dict[attr] = getattr(agg.client, attr)
                
            aggregates.append(agg_dict)
            
        print dumps(
            {"aggregates": aggregates, "projects": projects}, indent=4)
