'''
Created on May 2, 2010

Contains functions to transform to and from RSpecs

@author: jnaous
'''

from xml.etree import cElementTree as et
from django.conf import settings
import re

RSPEC_TAG = "rspec"
NETWORK_TAG = "network"
LINKS_TAG = "links"
LINK_TAG = "link"
SWITCHES_TAG = "switches"
SWITCH_TAG = "switch"
PORT_TAG = "port"

URN = "urn"
SRC_URN = "src_urn"
DST_URN = "dst_urn"

LOCATION = "location"
NAME = "name"
FLOWVISOR_URL = "flowvisor_url"

SWITCH_URN_REGEX = r"^%s\+switch:(?P<dpid>[\d:a-fA-F]+)$" % \
    settings.OPENFLOW_GAPI_RSC_URN_PREFIX.replace("+", r"\+")
PORT_URN_REGEX = r"%s\+port:(?P<port>\d+)$" % SWITCH_URN_REGEX[:-1]

switch_re = re.compile(SWITCH_URN_REGEX)
port_re = re.compile(PORT_URN_REGEX)

class BadURNError(Exception):
    def __init__(self, urn):
        super(Exception, self).__init__(
            "Unknown or badly formatted URN '%s'." % urn)
    

def _dpid_to_urn(dpid):
    """
    Change the dpid into a URN.
    """
    return "%s+switch:%s" % (settings.OPENFLOW_GAPI_RSC_URN_PREFIX, dpid)

def _urn_to_dpid(urn):
    """
    Change from a switch URN to a dpid.
    """
    m = switch_re.search(urn)
    
    if not m:
        raise BadURNError(urn)
    
    return m.group('dpid')

def _port_to_urn(dpid, port):
    """
    Specify an interface as URN.
    """
    
    return "%s+port:%s" % (_dpid_to_urn(dpid), port)

def _urn_to_port(urn):
    """
    Get the dpid and port from a urn specifiying a port.
    """

    m = port_re.search(urn)
    if not m:
        raise BadURNError(urn)
    
    return (m.group('dpid'), int(m.group('port')))

def _get_root_node(slice_urn, available):
    '''Create the root node and add all aggregates'''
    from openflow.plugin.models import OpenFlowAggregate
    root = et.Element(RSPEC_TAG)
    aggregates = OpenFlowAggregate.objects.filter(
        available=True).exclude(
            name__in=getattr(settings, "OPENFLOW_GAPI_FILTERED_AGGS", []))
    for aggregate in aggregates:
        _add_aggregate_node(root, aggregate, slice_urn, available)
    return root

def _add_aggregate_node(parent_elem, aggregate, slice_urn, available):
    '''Add an aggregate and the switches and links'''
    
    agg_elem = et.SubElement(
        parent_elem, NETWORK_TAG, {
            LOCATION: aggregate.location,
            NAME: aggregate.name,
        },
    )

    _add_switches_node(agg_elem, aggregate, slice_urn, available)
    _add_links_node(agg_elem, aggregate, slice_urn, available)
    
    return agg_elem

def _add_switches_node(parent_elem, aggregate, slice_urn, available):
    '''Add the switches tag and all switches'''
    from openflow.plugin.models import OpenFlowSwitch
    
    switches_elem = et.SubElement(parent_elem, SWITCHES_TAG)
    
    switches = OpenFlowSwitch.objects.filter(aggregate=aggregate)

    if slice_urn:
        switches = switches.filter(gapislice__slice_urn=slice_urn)
    elif available != None:
        switches = switches.filter(available=available)

    for switch in switches:
        switch_elem = et.SubElement(
            switches_elem, SWITCH_TAG, {
                URN: _dpid_to_urn(switch.datapath_id),
            },
        )
        _add_ports(switch_elem, switch)
        
    return switches_elem

def _add_ports(switch_elem, switch):
    """Add the ports tags for the switch"""
    for iface in switch.openflowinterface_set.all():
        et.SubElement(
            switch_elem, PORT_TAG, {
                URN: _port_to_urn(switch.datapath_id, iface.port_num),
            }
        )

def _add_links_node(parent_elem, aggregate, slice_urn, available):
    '''Add the links tag and all the links'''
    
    links_elem = et.SubElement(parent_elem, LINKS_TAG)

    if slice_urn:
        # TODO: don't know what particular links are in the slice (yet).
        return links_elem
    
    # Only available links are known
    links = aggregate.get_raw_topology()
    
    for s_dp, s_p, d_dp, d_p in links:
        et.SubElement(
            links_elem, LINK_TAG, {
                SRC_URN: _port_to_urn(s_dp, s_p),
                DST_URN: _port_to_urn(d_dp, d_p),
            },
        )
    return links_elem

def get_resources(slice_urn, geni_available):
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
    
    - C{src_urn}: identifier for the src port
    - C{dst_urn}: identifier for the dst port
    
    Currently no other attributes are defined through there may be more later.
    
    C{<switches>} has a list of C{<switch>} nodes with the following attributes:
    
    - C{urn}: urn prefix for a switch:datapathid
    
    Currently no other attributes are defined through there may be more later.
    
    For example::
    
    <rspec>
        <network name="Stanford" location="Stanford, CA, USA">
            <switches>
                <switch urn="urn:publicid:IDN+openflow:stanford+switch:0">
                    <port urn="urn:publicid:IDN+openflow:stanford+switch:0+port:0 />
                    <port urn="urn:publicid:IDN+openflow:stanford+switch:0+port:1 />
                </switch>
                <switch urn="urn:publicid:IDN+openflow:stanford+switch:1">
                    <port urn="urn:publicid:IDN+openflow:stanford+switch:1+port:0 />
                    <port urn="urn:publicid:IDN+openflow:stanford+switch:1+port:1 />
                </switch>
                <switch urn="urn:publicid:IDN+openflow:stanford+switch:2">
                    <port urn="urn:publicid:IDN+openflow:stanford+switch:2+port:0 />
                    <port urn="urn:publicid:IDN+openflow:stanford+switch:2+port:1 />
                </switch>
            </switches>
            <links>
                <link
                 src_urn="urn:publicid:IDN+openflow:stanford+switch:0+port:0
                 dst_urn="urn:publicid:IDN+openflow:stanford+switch:1+port:0
                />
                <link
                 src_urn="urn:publicid:IDN+openflow:stanford+switch:1+port:0
                 dst_urn="urn:publicid:IDN+openflow:stanford+switch:0+port:0
                />
                <link
                 src_urn="urn:publicid:IDN+openflow:stanford+switch:0+port:1
                 dst_urn="urn:publicid:IDN+openflow:stanford+switch:2+port:0
                />
                <link
                 src_urn="urn:publicid:IDN+openflow:stanford+switch:2+port:0
                 dst_urn="urn:publicid:IDN+openflow:stanford+switch:0+port:1
                />
                <link
                 src_urn="urn:publicid:IDN+openflow:stanford+switch:1+port:1
                 dst_urn="urn:publicid:IDN+openflow:stanford+switch:2+port:1
                />
                <link
                 src_urn="urn:publicid:IDN+openflow:stanford+switch:2+port:1
                 dst_urn="urn:publicid:IDN+openflow:stanford+switch:1+port:1
                />
            </links>
        </network>
        <network name="Princeton" location="USA">
            <switches>
                <switch urn="urn:publicid:IDN+openflow:stanford+switch:3">
                    <port urn="urn:publicid:IDN+openflow:stanford+switch:3+port:0 />
                </switch>
                <switch urn="urn:publicid:IDN+openflow:stanford+switch:4">
                    <port urn="urn:publicid:IDN+openflow:stanford+switch:4+port:0 />
                </switch>
            </switches>
            <links>
                <link
                 src_urn="urn:publicid:IDN+openflow:stanford+switch:3+port:0
                 dst_urn="urn:publicid:IDN+openflow:stanford+switch:4+port:0
                />
                <link
                 src_urn="urn:publicid:IDN+openflow:stanford+switch:4+port:0
                 dst_urn="urn:publicid:IDN+openflow:stanford+switch:3+port:0
                />
            </links>
        </network>
    </rspec>
    
    specifies a triangular graph at the Stanford network and a single link
    at the Princeton network
    '''
    
    root = _get_root_node(slice_urn, geni_available)
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
            firstname="John"
            lastname="Doe"
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
                <switch urn="urn:publicid:IDN+openflow:stanford+switch:0">
                <switch urn="urn:publicid:IDN+openflow:stanford+switch:2">
            </switches>
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
                <switch urn="urn:publicid:IDN+openflow:stanford+switch:1">
            </switches>
            <tp_src from="100" to="100" />
            <tp_dst from="100" to="*" />
        </flowspace>
    </resv_rspec>
    
    Any missing fields from the flowspace mean wildcard. All '*' means any
    value.
    
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
    
    from openflow.plugin.models import OpenFlowSwitch
    
    flowspace_elems = root.findall(".//%s" % FLOWSPACE_TAG)
    
    dpid_fs_map = {}
    
    for flowspace_elem in flowspace_elems:
#        print "parsing fs %s" % et.tostring(flowspace_elem)
        fs = {}
        # get a dict of the flowspace rule
        for tag in PORT_TAG, DL_SRC_TAG, DL_DST_TAG,\
        DL_TYPE_TAG, VLAN_ID_TAG, NW_SRC_TAG, NW_DST_TAG, NW_PROTO_TAG,\
        TP_SRC_TAG, TP_DST_TAG:
            from_key = "%s_start" % tag
            to_key = "%s_end" % tag
            field_elem = flowspace_elem.find(tag)
            if field_elem != None:
                fs[from_key] = field_elem.get("from")
                fs[to_key] = field_elem.get("to")
            else:
                fs[from_key] = WILDCARD
                fs[to_key] = WILDCARD
        
        # now for each switch, add a mapping from the dpid to the fs
        for switch_elem in flowspace_elem.find(SWITCHES_TAG).findall(SWITCH_TAG):
            dpid = _urn_to_dpid(switch_elem.get(URN))
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
