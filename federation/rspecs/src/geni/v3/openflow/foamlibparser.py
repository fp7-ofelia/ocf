from cStringIO import StringIO
from lxml import etree as ET
from rspecs.src.geni.v3.openflow.container.flowspace import FlowSpace
from rspecs.src.geni.v3.openflow.container.controller import Controller
from rspecs.src.geni.v3.openflow.container.group import Group
from rspecs.src.geni.v3.openflow.container.match import Match
from rspecs.src.geni.v3.openflow.container.dpid import DPID
from rspecs.src.geni.v3.openflow.container.port import Port

class FOAMLibParser:
    
    def __init__(self):
        self.OFNSv3 = "http://www.geni.net/resources/rspec/ext/openflow/3"
    
    def parse_request(self, rspec):
        
        s = StringIO(rspec)
        dom = ET.parse(s)
         
        sliver_dom = dom.find('{%s}sliver' % (self.OFNSv3))
        controller_elems = sliver_dom.findall('{%s}controller' % (self.OFNSv3))
        groups = sliver_dom.findall('{%s}group' % (self.OFNSv3))
        matches_dom = sliver_dom.findall('{%s}match' % (self.OFNSv3))
        
        flowspace = self.__parse_sliver(sliver_dom)  
        controller = self.__parse_controller(controller_elems)
        groups = self.__parse_groups(groups)
        matches = self.__parse_matches(matches_dom)
        
        
        #vlinks = sliver_dom.findall('{%s}vlink' % (self.OFNSv3))
        #for virtuallink in vlinks:
        #    vl = self.parseVirtualLink(virtuallink, self.OFNSv3)
        #    self.addVirtualLink(vl)
            
    def __parse_sliver(self, sliver_dom):
        if sliver_dom is None:
            raise Exception("No Sliver Defined")
        flowspace = FlowSpace()
        flowspace.set_email(sliver_dom.get("email", None))
        flowspace.set_description(sliver_dom.get("description", None))
        flowspace.set_ref = sliver_dom.get("ref", None)
        return flowspace
        
    def __parse_controller(self, controller_elems):
        controller = Controller()
        if controller_elems is None:
            raise Exception("No Controller Defined")#NoControllersDefined()
        controller_elems = controller_elems[0]
        controller.set_type(controller_elems.get("type"))
        controller.parse_url(controller_elems.get("url"))
        return controller
        
    def __parse_groups(self, groups):
        groups = list()
        for grp in groups:
            group = Group()
            dplist = []
            grpname = grp.get("name")
            if grpname is None:
                raise Exception("No grup name for group")#NoGroupName()
            datapaths = grp.findall('{%s}datapath' % (self.OFNSv3))
            for dp in datapaths:
                dplist.append(self.__parse_datapth(dp))
            group.set_name(grpname)
            group.set_dpids(dplist)    
            groups.append(group)
        return groups
    
    def __parse_datapath(self, dpid_dom):
        cmid = dpid_dom.get("component_manager_id")
        #if self.component_id.count(cmid[:-12]) != 1:
        #   raise ComponentManagerIDMismatch(self.component_id, cmid)
        #if cmid != getManagerID():
        #   raise UnknownComponentManagerID(self.component_id)
        dpid = DPID()
        dpid.set_component_manager_id(cmid)
        ports = list()
        for port_dom in dpid_dom.findall('{%s}port' % (self.OFNSv3)):
            p = Port()
            p.set_num(int(port_dom.get("num")))
            p.set_name(str(port_dom.get("name")))
            ports.add(p)
        dpid.set_ports(ports)
        return dpid    
        
    def __parse_matches(self, matches_dom, ns):
        matches = list()
        group_dom = matches_dom.find("{%s}use-group" % (ns))
        group_name = group_dom.get("name")
        packet_dom = matches_dom.find("{%s}packet" % (ns))
        for flowspec in packet_dom:
            match = Match()
            match.set_group(group_name)
            
            nodes = flowspec.findall('{%s}dl_src' % (ns))
            for dls in nodes:
                macstr = dls.get("value").strip()
                match.set_dl_src(macstr)

            nodes = flowspec.findall('{%s}dl_dst' % (ns))
            for dld in nodes:
                macstr = dld.get("value").strip()
                match.set_dl_dst(macstr)

            nodes = flowspec.findall('{%s}dl_type' % (ns))
            for dlt in nodes:
                dltstr = dlt.get("value").strip()
                match.set_dl_type(dltstr)

            nodes = flowspec.findall('{%s}dl_vlan' % (ns))
            for elem in nodes:
                vlidstr = elem.get("value").strip()
                match.set_dl_vlan(vlidstr)

            nodes = flowspec.findall('{%s}nw_src' % (ns))
            for elem in nodes:
                nwstr = elem.get("value").strip()
                match.set_nw_src(nwstr)

            nodes = flowspec.findall('{%s}nw_dst' % (ns))
            for elem in nodes:
                nwstr = elem.get("value").strip()
                match.set_nw_dst(nwstr)

            nodes = flowspec.findall('{%s}nw_proto' % (ns))
            for elem in nodes:
                nwproto = elem.get("value").strip()
                match.set_nw_proto(nwproto)

            nodes = flowspec.findall('{%s}tp_src' % (ns))
            for elem in nodes:
                tpsrc = elem.get("value").strip()
                match.set_tp_src(tpsrc)

            nodes = flowspec.findall('{%s}tp_dst' % (ns))
            for elem in nodes:
                tpdst = elem.get("value").strip()
                match.set_tp_dst(tpdst)
            
            matches.append(match)
            