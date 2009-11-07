'''
Created on Oct 17, 2009

@author: jnaous
'''

import elementtree.ElementTree as et
from elementtree.ElementTree import ElementTree 
import models
from django.db.models import Count
import egeni_api

PLNODE_DEFAULT_IMG = "/img/server-2u-rev.png"

en_debug = 0
def debug(s):
    if(en_debug):
        print(s)

def reserve_slice(am_url, rspec, slice_id):
    '''
    Reserves the slice identified by slice_id or
    updates the slice if already reserved on the AM.
    
    On success, returns the empty string.
    On error, returns an rspec that has the failing nodes with their
    failing interfaces if the AM failed to reserve the interface.
    If reserving the node failed but not due to the interface, the
    rspec contains only the failing node without its interfaces.
    '''
    
#    return egeni_api.reserve_slice(am_url, rspec, slice_id)
    print "Reserving PL Slice: %s" % rspec

def delete_slice(am_url, slice_id):
    '''
    Delete the slice.
    '''
#    return egeni_api.delete_slice(am_url, slice_id)

def get_rspec(am_url):
    '''
    Returns the RSpec of available resources.
    '''
#    return '''<?xml version="1.0" encoding="UTF-8"?>
#<RSpec start_time="1235696400" duration="2419200">
#    <networks>
#        <NetSpec name="planetlab.us" start_time="1235696400" duration="2419200">
#            <nodes>
#                <NodeSpec name="planetlab-1.cs.princeton.edu" type="" init_params="" cpu_min="" cpu_share="" cpu_pct="" disk_max="" start_time="" duration="">
#                    <net_if>
#                        <IfSpec name="128.112.139.71" addr="128.112.139.71" type="ipv4" init_params="" min_rate="0" max_rate="10000000" max_kbyte="" ip_spoof="" />
#                    </net_if>
#                </NodeSpec>
#                <NodeSpec name="planetlab-2.cs.princeton.edu" type="" init_params="" cpu_min="" cpu_share="" cpu_pct="" disk_max="" start_time="" duration="">
#                    <net_if>
#                        <IfSpec name="128.112.139.72" addr="128.112.139.72" type="ipv4" init_params="" min_rate="0" max_rate="10000000" max_kbyte="" ip_spoof="" />
#                        <IfSpec name="128.112.139.120" addr="128.112.139.120" type="proxy" init_params="" min_rate="0" max_rate="" max_kbyte="" ip_spoof="" />
#                        <IfSpec name="128.112.139.119" addr="128.112.139.119" type="proxy" init_params="" min_rate="0" max_rate="" max_kbyte="" ip_spoof="" />
#                    </net_if>
#                </NodeSpec>
#            </nodes>
#        </NetSpec>
#        <NetSpec name="planetlab.eu" start_time="" duration="">
#            <nodes>
#                <NodeSpec name="onelab03.onelab.eu" type="" init_params="" cpu_min="" cpu_share="" cpu_pct="" disk_max="" start_time="" duration="">
#                    <net_if>
#                        <IfSpec name="128.112.139.321" addr="128.112.139.321" type="ipv4" init_params="" min_rate="0" max_rate="10000000" max_kbyte="" ip_spoof="" />
#                    </net_if>
#                </NodeSpec>
#            </nodes>
#        </NetSpec>
#    </networks>
#</RSpec>
#'''

    return egeni_api.get_rspec(am_url)

def update_rspec(self_am):
    '''
    Read and parse the RSpec specifying all 
    nodes from the aggregate manager using the E-GENI
    RSpec
    '''
    
    xml_str = get_rspec(self_am.url)
    tree = ElementTree(et.fromstring(xml_str))
    
    debug("Parsing xml:")
    debug(xml_str)

    # keep track of created ids to delete old ones
    node_ids = []
    iface_ids = []
    for netspec_elem in tree.findall("*/NetSpec"):
        netspec_name = netspec_elem.get("name")
        
        for node_elem in netspec_elem.findall("*/NodeSpec"):
            debug("found node elem %s" % node_elem)
            name = node_elem.get("name")
            debug("name: %s" % name)
            type = models.AggregateManager.TYPE_PL
            n = models.Node.objects.filter(type=type)
            debug("Get: %s" % n)
            node, created = models.Node.objects.get_or_create(
                          nodeId=name,
                          defaults={"nodeId": name,
                                    "name": name,
                                    "type": type,
                                    "is_remote": False,
                                    "remoteURL": self_am.url,
                                    "aggMgr": self_am,
                                    "img_url": PLNODE_DEFAULT_IMG,
                                    "extra_context": "netspec__name=%s" % netspec_name,
                                    }
                          )
            
            debug("Node new: %s" % created)
            
            if not created:
                node.remoteURL = self_am.url
                node.aggMgr = self_am
            
            self_am.connected_node_set.add(node)
            node.save()
            node_ids.append(node.nodeId)
            
            # add all the interfaces
            for i, iface_elem in enumerate(node_elem.findall("*/IfSpec")):
                kwargs = {}
                for attrib in ("name", "addr", "type", #"init_params",
#                               "min_rate", "max_rate", "max_kbyte",
#                               "ip_spoof",
                               ):
                    kwargs[attrib] = iface_elem.get(attrib)
                
                # TODO: port nums
                kwargs["portNum"] = i
                
                # TODO: How do they maintain a consistent mapping of iface
                # to identifier e.g. when addresses change. Is name consistent?
                iface, created = models.Interface.objects.get_or_create(
                            name=kwargs["name"],
                            ownerNode=node,
                            defaults=kwargs,
                            )
                
                if not created:
                    for fld in kwargs:
                        iface.__setattr__(fld, kwargs[fld])
                    iface.save()
            
                iface_ids.append(iface.id)
    
    debug("Added nodes %s" % node_ids)
    
    # delete all the old stuff
    for n in models.Node.objects.filter(aggMgr=self_am).exclude(nodeId__in=node_ids):
        debug("Deleting %s " % n.nodeId)
        
    models.Node.objects.filter(
        aggMgr=self_am).exclude(
            nodeId__in=node_ids).delete()
    models.Interface.objects.filter(
        ownerNode__aggMgr=self_am).exclude(
            id__in=iface_ids).delete()
