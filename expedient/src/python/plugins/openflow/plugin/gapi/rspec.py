'''
Created on May 2, 2010

Contains functions to transform to and from RSpecs

@author: jnaous
'''

from xml.etree import ElementTree as et
from django.conf import settings
from django.db.models import Q
import re
from expedient.clearinghouse.users.models import UserProfile
from openflow.plugin.models import OpenFlowSwitch, FlowSpaceRule
from expedient.common.federation.geni.util.urn_util import publicid_to_urn
from expedient.clearinghouse.aggregate.models import Aggregate
from expedient.common.tests.utils import drop_to_shell
import time

RSPEC_TAG = "rspec"
NETWORK_TAG = "network"
LINKS_TAG = "links"
LINK_TAG = "link"
SWITCHES_TAG = "switches"
SWITCH_TAG = "switch"
PORT_NUM_TAG = "port_num"
PORT_TAG = "port"

VERSION = "version"

CURRENT_ADV_VERSION = "2"

URN = "urn"
SRC_URN = "src_urn"
DST_URN = "dst_urn"

LOCATION = "location"
NAME = "name"
FLOWVISOR_URL = "flowvisor_url"

OPENFLOW_GAPI_RSC_URN_PREFIX = publicid_to_urn(
    "IDN %s//%s" % (settings.GCF_BASE_NAME, settings.OPENFLOW_GCF_BASE_SUFFIX)
)

SWITCH_URN_REGEX = r"^%s\+switch:(?P<dpid>[\d:a-fA-F]+)$" % \
    OPENFLOW_GAPI_RSC_URN_PREFIX.replace("+", r"\+")
PORT_URN_REGEX = r"%s\+port:(?P<port>\d+)$" % SWITCH_URN_REGEX[:-1]

switch_re = re.compile(SWITCH_URN_REGEX)
port_re = re.compile(PORT_URN_REGEX)

EXTERNAL_SWITCH_URN_REGEX = r"^(?P<prefix>.*)\+switch:(?P<dpid>[:a-fA-F\d]+)$"
EXTERNAL_PORT_URN_REGEX = r"%s\+port:(?P<port>\d+)$" % EXTERNAL_SWITCH_URN_REGEX[:-1]

external_switch_re = re.compile(EXTERNAL_SWITCH_URN_REGEX)
external_port_re = re.compile(EXTERNAL_PORT_URN_REGEX)

class BadURNError(Exception):
    def __init__(self, urn, error = None):
        self.urn = urn
        if error:
            msg = " Error was: %s" % error
        else:
            msg = ""
        super(Exception, self).__init__(
            "Unknown or badly formatted URN '%s'.%s" % (urn, msg))
    
class UnknownObject(Exception):
    def __init__(self, klass, id, tag):
        self.klass = klass
        self.id = id
        self.tag = tag
        super(Exception, self).__init__(
            "Could not find the %s object with id %s of element tag %s in the"
            " database." % (klass, id, tag)
        )
        

def _dpid_to_urn(dpid):
    """
    Change the dpid into a URN.
    """
    return "%s+switch:%s" % (OPENFLOW_GAPI_RSC_URN_PREFIX, dpid)

def _urn_to_dpid(urn):
    """
    Change from a switch URN to a dpid.
    """
    m = external_switch_re.search(urn)
    
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

    m = external_port_re.search(urn)
    if not m:
        raise BadURNError(urn)
    
    return (m.group('dpid'), int(m.group('port')))

def _get_root_node(slice_urn, available):
    '''Create the root node and add all aggregates'''
    # break circular dependecies by putting imports inside function
    from openflow.plugin.models import OpenFlowAggregate
    from expedient.clearinghouse.geni.gopenflow.models import GCFOpenFlowAggregate
    
    root = et.Element(
        RSPEC_TAG, {
            "type": "openflow", VERSION: CURRENT_ADV_VERSION})
    aggregates = Aggregate.objects.filter_for_classes(
        [OpenFlowAggregate, GCFOpenFlowAggregate]).filter(
            available=True).exclude(
                name__in=getattr(settings, "OPENFLOW_GAPI_FILTERED_AGGS", []))
    
    for aggregate in aggregates:
        aggregate = aggregate.as_leaf_class()
        _add_aggregate_node(
            root, aggregate, slice_urn, available)
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
    
    switches_elem = et.SubElement(parent_elem, SWITCHES_TAG)
    
    switches = OpenFlowSwitch.objects.filter(aggregate=aggregate)

    if available != None:
        switches = switches.filter(available=available)

    for switch in switches:
        switch_elem = et.SubElement(
            switches_elem, SWITCH_TAG, {
                URN: _dpid_to_urn(switch.datapath_id),
            },
        )
        _add_ports(switch_elem, switch, slice_urn)
        
    return switches_elem

def _add_ports(switch_elem, switch, slice_urn):
    """Add the ports tags for the switch"""
    
    ifaces = switch.openflowinterface_set.all()
        
    for iface in ifaces:
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
    
        <rspec type="openflow" version="2">
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
FIRSTNAME="firstname"
LASTNAME="lastname"
AFFILIATION="affiliation"
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
EXPIRY="expiry"

CURRENT_RESV_VERSION="2"

def parse_slice(resv_rspec):
    '''
    Parses the reservation RSpec and returns a tuple:
    C{(project_name, project_desc, slice_name, slice_desc, 
    controller_url, firstname, lastname, affiliation, email, password,
    slivers)} where C{slivers}
    is a dict mapping OpenFlowInterface instances to a flowspace
    dict for reservation on them.
    
    In the flowspace definition, specifying a "switch" element adds all
    interfaces on that switch. Otherwise, specifying ports adds only that
    port on the switch.
    
    The reservation rspec looks like the following::
    
        <resv_rspec type="openflow" version="2">
            <user
                firstname="John"
                lastname="Doe"
                affiliation="Stanford"
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
                expiry="1298020775"
            />
            <flowspace>
                <switch urn="urn:publicid:IDN+openflow:stanford+switch:0" />
                <port urn="urn:publicid:IDN+openflow:stanford+switch:2+port:1 />
                <port urn="urn:publicid:IDN+openflow:stanford+switch:2+port:2 />
                <port urn="urn:publicid:IDN+openflow:stanford+switch:2+port:3 />
                <dl_src from="22:33:44:55:66:77" to="22:33:44:55:66:77" />
                <dl_type from="0x800" to="0x800" />
                <vlan_id from="15" to="20" />
                <nw_src from="192.168.3.0" to="192.168.3.255" />
                <nw_dst from="192.168.3.0" to="192.168.3.255" />
                <nw_proto from="17" to="17" />
                <tp_src from="100" to="100" />
                <tp_dst from="100" />
            </flowspace>
            <flowspace>
                <switch urn="urn:publicid:IDN+openflow:stanford+switch:1" />
                <tp_src from="100" to="100" />
                <tp_dst from="100" />
            </flowspace>
        </resv_rspec>
    
    Any missing fields from the flowspace mean wildcard. All '*' means any
    value.
    
    The available fields are::
        
        dl_src, dl_dst, dl_type, vlan_id, nw_src,
        nw_dst, nw_proto, tp_src, tp_dst
    
    All integers can by specified as hex or decimal.
    '''
    
    # Parse the rspec
    root = et.fromstring(resv_rspec)
    version = root.get(VERSION, "unknown")
    if version != CURRENT_RESV_VERSION:
        raise Exception(
            "Can only parse reservation rspecs"
            " version 2. Given rspec version "
            "is %s" % version)
    
    firstname, lastname, affiliation, email, password = \
        _resv_parse_user(root)
    slice_name, slice_desc, slice_expiry, controller_url = _resv_parse_slice(root)
    project_name, project_desc = _resv_parse_project(root)
    slivers = _resv_parse_slivers(root)
    
    return (project_name, project_desc, slice_name, slice_desc,
            slice_expiry, 
            controller_url, firstname, lastname, affiliation,
            email, password, slivers)

def _resv_parse_user(root):
    '''parse the user tag from the root Element'''
    user_elem = root.find(USER_TAG)
    return (user_elem.get(FIRSTNAME), user_elem.get(LASTNAME),
            user_elem.get(AFFILIATION),
            user_elem.get(EMAIL), user_elem.get(PASSWORD))

def _resv_parse_slice(root):
    slice_elem = root.find(SLICE_TAG)
    return (slice_elem.get(NAME),
            slice_elem.get(DESCRIPTION),
            long(slice_elem.get(EXPIRY)),
            slice_elem.get(CONTROLLER))
    
def _resv_parse_project(root):
    proj_elem = root.find(PROJECT_TAG)
    return (proj_elem.get(NAME), proj_elem.get(DESCRIPTION))

def _resv_parse_slivers(root):
    '''Return a list of slivers where slivers is a list of tuples
    of (flowspace dict, OpenFlowInterface queryset).'''
    
    from openflow.plugin.models import OpenFlowInterface
    
    flowspace_elems = root.findall(".//%s" % FLOWSPACE_TAG)
    
    port_fs_map = []
    
    for flowspace_elem in flowspace_elems:
        fs = {}
        
        # get a dict of the flowspace rule
        for tag in DL_SRC_TAG, DL_DST_TAG,\
        DL_TYPE_TAG, VLAN_ID_TAG, NW_SRC_TAG, NW_DST_TAG, NW_PROTO_TAG,\
        TP_SRC_TAG, TP_DST_TAG:
            from_key = "%s_start" % tag
            to_key = "%s_end" % tag
            field_elem = flowspace_elem.find(tag)
            if field_elem != None:
                fs[from_key] = field_elem.get("from", None)
                fs[to_key] = field_elem.get("to", None)
        
        # now get the interfaces
        interface_q = None
        switch_elems = flowspace_elem.findall(".//%s" % SWITCH_TAG)
        for switch_elem in switch_elems:
            # get the switch
            dpid = _urn_to_dpid(switch_elem.get("urn"))
            # get the interfaces
            new_q = Q(switch__datapath_id=dpid)
            interface_q = interface_q | new_q if interface_q else new_q
            
        port_elems = flowspace_elem.findall(".//%s" % PORT_TAG)
        for port_elem in port_elems:
            # get the switch and port
            dpid, port_num = _urn_to_port(port_elem.get("urn"))
            # get the interfaces
            new_q = Q(switch__datapath_id=dpid, port_num=port_num)
            interface_q = interface_q | new_q if interface_q else new_q
            
        port_fs_map.append((fs, OpenFlowInterface.objects.filter(interface_q)))
        
    return port_fs_map

def create_resv_rspec(user, slice, aggregate=None):
    """Create a reservation rspec from the set of interface slivers.
    
    @param user: The user making the reservation.
    @type user: L{django.contrib.auth.models.User}
    @param slice: The slice to use in the reservation.
    @type slice: L{expedient.clearinghouse.slice.models.Slice}
    @keyword aggregate: If not None, only get the resv rspec for the
        specified aggregate. DDefault is None.
    @type aggregate: None or L{openflow.plugin.models.OpenFlowAggregate}
    
    @return: an OpenFlow reservation RSpec for the wanted slivers.
    @rtype: C{str}
    """
    
    root = et.Element(
        RESV_RSPEC_TAG, {"type": "openflow", VERSION: CURRENT_RESV_VERSION})
    
    # add the user info
    et.SubElement(
        root, USER_TAG, {
            FIRSTNAME: user.first_name,
            LASTNAME: user.last_name,
            AFFILIATION: UserProfile.get_or_create_profile(user).affiliation,
            EMAIL: user.email,
            PASSWORD: slice.openflowsliceinfo.password,
        }
    )
    
    # add the project info
    et.SubElement(
        root, PROJECT_TAG, {
            NAME: slice.project.name,
            DESCRIPTION: slice.project.description,
        }
    )
    
    # add the slice info
    et.SubElement(
        root, SLICE_TAG, {
            NAME: slice.name,
            DESCRIPTION: slice.description,
            EXPIRY: "%s" % long(time.mktime(slice.expiration_date.timetuple())),
            CONTROLLER: slice.openflowsliceinfo.controller_url,
        }
    )
    
    flowspace_qs = FlowSpaceRule.objects.filter(
        slivers__slice=slice).distinct()
    if aggregate:
        flowspace_qs = flowspace_qs.filter(
            slivers__resource__aggregate__id=aggregate.id).distinct()
        
    # add the flowspace
    for fs in flowspace_qs:
        fs_elem = et.SubElement(root, FLOWSPACE_TAG)
        for sliver in fs.slivers.all():
            iface = sliver.resource.as_leaf_class()
            et.SubElement(
                fs_elem, PORT_TAG, {
                    URN: _port_to_urn(iface.switch.datapath_id, iface.port_num)
                }
            )
            
        for tag in DL_SRC_TAG, DL_DST_TAG,\
        DL_TYPE_TAG, VLAN_ID_TAG, NW_SRC_TAG, NW_DST_TAG, NW_PROTO_TAG,\
        TP_SRC_TAG, TP_DST_TAG:
            f = getattr(fs, "%s_start" % tag)
            t = getattr(fs, "%s_end" % tag)
            d = {}
            if f is not None and f != "":
                d["from"] =  str(f)
            if t is not None and t != "": 
                d["to"] = str(t)
            if d:
                et.SubElement(
                    fs_elem, tag, d,
                )
    
    return et.tostring(root)

def parse_external_rspec(rspec):
    """Parse the given rspec and create dicts of the given switches.
    
    Parses the RSpec and creates a dict mapping switches to the ports they
    have. It also creates a list of (dpid, port, dpid, port) describing the
    links.
    
    @param rspec: The advertisement RSpec
    @type rspec: XML C{str}
    @return: tuple of a dict mapping datapath ID strings to list of port
        numbers and a list of
        (src dpid, src port num, dst dpid, dst port num, attrs)
        describing the links.
    @rtype: (C{dict} mapping C{str} to C{list} of C{int},
        C{list} of (C{str}, C{int}, C{str}, C{int}, C{dict}))
    """
    
    root = et.fromstring(rspec)
    
    switch_elems = root.findall(".//%s" % SWITCH_TAG)
    switches = {}
    for switch_elem in switch_elems:
        urn = switch_elem.get(URN)
        dpid = _urn_to_dpid(urn)
        switches[dpid] = []
    
    port_elems = root.findall(".//%s" % PORT_TAG)
    for port_elem in port_elems:
        urn = port_elem.get(URN)
        dpid, port = _urn_to_port(urn)
        try:
            switches[dpid].append(port)
        except KeyError:
            raise Exception("No switch with datapath ID %s found"
                            " for port with URN %s" % (dpid, urn))
        
    link_elems = root.findall(".//%s" % LINK_TAG)
    links = []
    for link_elem in link_elems:
        src_urn = link_elem.get(SRC_URN)
        dst_urn = link_elem.get(DST_URN)
        src_dpid, src_port = _urn_to_port(src_urn)
        dst_dpid, dst_port = _urn_to_port(dst_urn)
        links.append((src_dpid, src_port, dst_dpid, dst_port, {}))
        
    return switches, links
