'''
Created on May 2, 2010

Contains functions to transform to and from RSpecs

@author: jnaous
'''

from xml.etree import cElementTree as et
from clearinghouse.openflow.models import OpenFlowAggregate, OpenFlowSwitch,\
    GAPISlice
from clearinghouse.slice.models import Slice

RSPEC_TAG = "rspec"
NETWORK_TAG = "network"
LINKS_TAG = "links"
LINK_TAG = "link"
SWITCHES_TAG = "switches"
SWITCH_TAG = "switch"

LOCATION = "location"
NAME = "name"
FLOWVISOR_URL = "flowvisor_url"
SRC_DPID = "src_dpid"
SRC_PORT = "src_port"
DST_DPID = "dst_dpid"
DST_PORT = "dst_port"
DPID = "dpid"

def _get_root_node():
    '''Create the root node and add all aggregates'''
    root = et.Element(RSPEC_TAG)
    for aggregate in OpenFlowAggregate.objects.all():
        _add_aggregate_node(root, aggregate)
    return root

def _add_aggregate_node(parent_elem, aggregate):
    '''Add an aggregate and the switches and links'''
    
    agg_elem = et.SubElement(
        parent_elem, LINKS_TAG, {
            LOCATION: aggregate.location,
            NAME: aggregate.name,
        },
    )

    _add_switches_node(agg_elem, aggregate)
    _add_links_node(agg_elem, aggregate)
    
    return agg_elem

def _add_switches_node(parent_elem, aggregate):
    '''Add the switches tag and all switches'''
    
    switches_elem = et.SubElement(parent_elem, SWITCHES_TAG)
    
    dpids = OpenFlowSwitch.objects.filter(
        aggregate=aggregate, available=True).values_list(
            "datapath_id", flat=True)
        
    for dpid in dpids:
        et.SubElement(
            switches_elem, SWITCH_TAG, {
                DPID: dpid,
            },
        )
    return switches_elem

def _add_links_node(parent_elem, aggregate):
    '''Add the links tag and all the links'''
    
    links_elem = et.SubElement(parent_elem, LINKS_TAG)
    
    links = aggregate.get_raw_topology()
    
    for s_dp, s_p, d_dp, d_p in links:
        et.SubElement(
            links_elem, LINK_TAG, {
                SRC_DPID: s_dp,
                SRC_PORT: s_p,
                DST_DPID: d_dp,
                DST_PORT: d_p,
            },
        )
    return links_elem

def get_all_resources():
    '''
    Gets a list of all the resources under all the aggregates as XML.
    
    The XML returned has a C{<rspec>} root node with no attributes.
    
    Under the rspec there is a list of C{<network>} elements with the following
    attributes:
    
    - C{location}: location
    - C{name}: name of the aggregate/network
    - C{flowvisor_url}: currently not implemented
    
    Under each C{<network>} there are exactly two nodes: C{<links>} and
    C{<nodes>}.
    
    C{<links>} has a list of C{<link>} nodes with the following attributes:
    
    - C{src_dpid}: the datapath id of the source switch.
    - C{src_port}: the number of the source switch's port.
    - C{dst_dpid}: the datapath id of the destination switch.
    - C{dst_port}: the number of the destination switch's port.
    
    Currently no other attributes are defined through there may be more later.
    
    C{<switches>} has a list of C{<switch>} nodes with the following attributes:
    
    - C{dpid}: the datapath id of the switch.
    
    Currently no other attributes are defined through there may be more later.
    
    For example::
    
    <rspec>
        <network name="Stanford" location="Stanford, CA, USA">
            <switches>
                <switch dpid="0" />
                <switch dpid="1" />
                <switch dpid="2" />
            </switches>
            <links>
                <link src_dpid="0" src_port="0" dst_dpid="1" dst_port="0" />
                <link src_dpid="1" src_port="0" dst_dpid="0" dst_port="0" />
                <link src_dpid="0" src_port="1" dst_dpid="2" dst_port="0" />
                <link src_dpid="2" src_port="0" dst_dpid="0" dst_port="1" />
                <link src_dpid="1" src_port="1" dst_dpid="2" dst_port="1" />
                <link src_dpid="2" src_port="1" dst_dpid="1" dst_port="1" />
            </links>
        </network>
    </rspec>
    
    specifies a triangular graph.
    '''
    
    root = _get_root_node()
    return et.tostring(root)

RESV_RSPEC_TAG="resv_rspec"
USER_TAG="user"
FULLNAME="fullname"
EMAIL="email"
PASSWORD="password"
PROJECT_TAG="project"
SLICE_TAG="slice"
DESCRIPTION="description"
CONTROLLER="controller_url"
FLOWSPACE_TAG="flowspace"
POLICY_TAG="policy"
PORT_TAG="port"
DL_SRC_TAG="dl_src"
DL_DST_TAG="dl_dst"
DL_TYPE_TAG="dl_type"
VLAN_ID_TAG="vlan_id"
NW_SRC_TAG="nw_src"
NW_DST_TAG="nw_dst"
NW_PROTO_TAG="nw_proto"
TP_SRC_TAG="tp_src"
TP_DST_TAG="tp_dst"
WILDCARD="*"

def parse_slice(resv_rspec):
    '''
    Parses the reservation RSpec and returns a tuple:
    (project_name, project_desc, slice_name, slice_desc, 
    controller_url, email, password, agg_slivers) where slivers
    is a list of (aggregate, slivers) tuples, and slivers is a dict suitable
    for use in the create_slice xml-rpc call of the opt-in manager.
    
    The reservation rspec looks like the following:
    
    <resv_rspec>
        <user
            fullname="John Doe"
            email="john.doe@geni.net"
            password="slice_pass"
        />
        <project
            name="Stanford Networking Group"
            description="Internet performance research to ..."
        />
        <slice
            name="Crazy Load Balancer"
            description="Does this and that..."
            controller_url="tcp:controller.stanford.edu:6633"
        />
        <flowspace>
            <switches>
                <switch dpid="0">
                <switch dpid="2">
            </switches>
            <policy value="1" />
            <port from="1" to="4" />
            <dl_src from="22:33:44:55:66:77" to="22:33:44:55:66:77" />
            <dl_dst from="*" to="*" />
            <dl_type from="0x800" to="0x800" />
            <vlan_id from="15" to="20" />
            <nw_src from="192.168.3.0" to="192.168.3.255" />
            <nw_dst from="192.168.3.0" to="192.168.3.255" />
            <nw_proto from="17" to="17" />
            <tp_src from="100" to="100" />
            <tp_dst from="100" to="*" />
        </flowspace>
        <flowspace>
            <switches>
                <switch dpid="1">
            </switches>
            <policy value="-1" />
            <tp_src from="100" to="100" />
            <tp_dst from="100" to="*" />
        </flowspace>
    </resv_rspec>
    
    Any missing fields from the flowspace mean wildcard. All '*' means any
    value. The policy can have the following values:

    - C{1}: Allow
    - C{-1}: Deny
    - C{0}: Read-only
    
    All integers can by specified as hex or decimal.
    '''
    
    # Parse the rspec
    root = et.fromstring(resv_rspec)
    email, password = _resv_parse_user(root)
    slice_name, slice_desc, controller_url = _resv_parse_slice(root)
    project_name, project_desc = _resv_parse_project(root)
    agg_slivers = _resv_parse_slivers(root)
    
    return (project_name, project_desc, slice_name, slice_desc, 
            controller_url, email, password, agg_slivers)

def _resv_parse_user(root):
    '''parse the user tag from the root Element'''
    user_elem = root.find(USER_TAG)
    return (user_elem.get(EMAIL), user_elem.get(PASSWORD))

def _resv_parse_slice(root):
    slice_elem = root.find(SLICE_TAG)
    return (slice_elem.get(NAME),
            slice_elem.get(DESCRIPTION),
            slice_elem.get(CONTROLLER))
    
def _resv_parse_project(root):
    proj_elem = root.find(PROJECT_TAG)
    return (proj_elem.get(NAME), proj_elem.get(DESCRIPTION))

def _resv_parse_slivers(root):
    '''Return a list of tuples (aggregate, slivers) where aggregate is
    an OpenFlowAggregate instance and slivers is a list of dicts suitable for
    use in the create_slice xml-rpc call of the OM'''
    
    flowspace_elems = root.findall(FLOWSPACE_TAG)
    
    dpid_fs_map = {}
    
    for flowspace_elem in flowspace_elems:
        
        fs = {}
        # get a dict of the flowspace rule
        for tag in POLICY_TAG, PORT_TAG, DL_SRC_TAG, DL_DST_TAG,\
        DL_TYPE_TAG, VLAN_ID_TAG, NW_SRC_TAG, NW_DST_TAG, NW_PROTO_TAG,\
        TP_SRC_TAG, TP_DST_TAG:
            from_key = "%s_start" % tag
            to_key = "%s_end" % tag
            field_elem = flowspace_elem.find(tag)
            if field_elem:
                fs[from_key] = field_elem.get["from"]
                fs[to_key] = field_elem.get["to"]
            else:
                fs[from_key] = WILDCARD
                fs[to_key] = WILDCARD
        
        # now for each switch, add a mapping from the dpid to the fs
        for switch_elem in flowspace_elem.find(SWITCHES_TAG).findall(SWITCH_TAG):
            dpid = switch_elem.get(DPID)
            if dpid not in dpid_fs_map:
                dpid_fs_map[dpid] = []
            dpid_fs_map[dpid].append(fs)
        
    datapaths = dpid_fs_map.keys()
    # get a list of all the available datapaths
    qs = OpenFlowSwitch.objects.filter(
        datapath_id__in=datapaths).select_related(
            "aggregate")
    
    # This is a map from aggregate pk to a tuple (openflow_aggregate, list of slivers)
    # each sliver is a list of dicts as described in the OM's create_slice call
    agg_slivers_map = {}
    for dp in qs:
        if dp.aggregate.pk not in agg_slivers_map:
            agg_slivers_map[dp.aggregate.pk] = (dp.aggregate.as_leaf_class(), [])
        agg_slivers_map[dp.aggregate.pk][1].append(
            {'datapath_id': dp.datapath_id,
             'flowspace': dpid_fs_map[dp.datapath_id]})
        
    return agg_slivers_map.values()
