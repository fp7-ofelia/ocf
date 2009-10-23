'''
Created on Oct 17, 2009

@author: jnaous
'''

import elementtree.ElementTree as et
from elementtree.ElementTree import ElementTree 
import models
from django.db.models import Count

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
    
    return ""    

def delete_slice(am_url, slice_id):
    '''
    Delete the slice.
    '''
    pass

def get_rspec(am_url):
    '''
    Returns the RSpec of available resources.
    '''
    return '''<?xml version="1.0" encoding="UTF-8"?>
<RSpec start_time="1235696400" duration="2419200">
    <networks>
        <NetSpec name="planetlab.us" start_time="1235696400" duration="2419200">
            <nodes>
                <NodeSpec name="planetlab-1.cs.princeton.edu" type="" init_params="" cpu_min="" cpu_share="" cpu_pct="" disk_max="" start_time="" duration="">
                    <net_if>
                        <IfSpec name="128.112.139.71" addr="128.112.139.71" type="ipv4" init_params="" min_rate="0" max_rate="10000000" max_kbyte="" ip_spoof="" />
                    </net_if>
                </NodeSpec>
                <NodeSpec name="planetlab-2.cs.princeton.edu" type="" init_params="" cpu_min="" cpu_share="" cpu_pct="" disk_max="" start_time="" duration="">
                    <net_if>
                        <IfSpec name="128.112.139.72" addr="128.112.139.72" type="ipv4" init_params="" min_rate="0" max_rate="10000000" max_kbyte="" ip_spoof="" />
                        <IfSpec name="128.112.139.120" addr="128.112.139.120" type="proxy" init_params="" min_rate="0" max_rate="" max_kbyte="" ip_spoof="" />
                        <IfSpec name="128.112.139.119" addr="128.112.139.119" type="proxy" init_params="" min_rate="0" max_rate="" max_kbyte="" ip_spoof="" />
                    </net_if>
                </NodeSpec>
            </nodes>
        </NetSpec>
        <NetSpec name="planetlab.eu" start_time="" duration="">
            <nodes>
                <NodeSpec name="onelab03.onelab.eu" type="" init_params="" cpu_min="" cpu_share="" cpu_pct="" disk_max="" start_time="" duration="">
                    <net_if>
                        <IfSpec name="128.112.139.321" addr="128.112.139.321" type="ipv4" init_params="" min_rate="0" max_rate="10000000" max_kbyte="" ip_spoof="" />
                    </net_if>
                </NodeSpec>
            </nodes>
        </NetSpec>
    </networks>
</RSpec>
'''

def update_rspec(self_am):
    '''
    Read and parse the RSpec specifying all 
    nodes from the aggregate manager using the E-GENI
    RSpec
    '''
    
    xml_str = get_rspec(self_am.url)
    tree = ElementTree(et.fromstring(xml_str))
    
    