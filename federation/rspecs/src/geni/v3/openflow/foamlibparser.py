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
        
        for group in groups:
            for match in matches:
                if group.get_name() == match.get_group():
                    group.add_match(match)
        flowspace.set_controller(controller)
        flowspace.set_groups(groups)
        return flowspace
        
        
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
        
    def __parse_groups(self, groups_dom):
        groups = list()
        for grp in groups_dom:
            group = Group()
            dplist = []
            grpname = grp.get("name")
            if grpname is None:
                raise Exception("No grup name for group")#NoGroupName()
            datapaths = grp.findall('{%s}datapath' % (self.OFNSv3))
            for dp in datapaths:
                dplist.append(self.__parse_datapath(dp))
            group.set_name(grpname)
            group.set_dpids(dplist)    
            groups.append(group)
        return groups
    
    def __parse_datapath(self, dpid_dom):
        component_manager_id = dpid_dom.get("component_manager_id")
        component_id = dpid_dom.get("component_id")
        datapath_id = dpid_dom.get("dpid")
       
        dpid = DPID()
        dpid.set_component_manager_id(component_manager_id)
        dpid.set_component_id(component_id)
        dpid.set_datapath(datapath_id)
        
        ports = list()
        for port_dom in dpid_dom.findall('{%s}port' % (self.OFNSv3)):
            p = Port()
            p.set_num(int(port_dom.get("num")))
            p.set_name(str(port_dom.get("name")))
            ports.append(p)
        dpid.set_ports(ports)
        return dpid    
        
    def __parse_matches(self, matches_dom):
        matches = list()
        for match_dom in matches_dom:
            group_dom = match_dom.find("{%s}use-group" % (self.OFNSv3))
            group_name = group_dom.get("name")
            match = self.__parse_flowspec(match_dom)
            match.set_group(group_name)
            matches.append(match)
        return matches
        
    def __parse_flowspec(self, match_dom):    
        packet_dom = match_dom.find("{%s}packet" % (self.OFNSv3))    
        
        match = Match()
            
        nodes = packet_dom.findall('{%s}dl_src' % (self.OFNSv3))
        for dls in nodes:
            macstr = dls.get("value").strip()             
            match.add_dl_src(macstr)

        nodes = packet_dom.findall('{%s}dl_dst' % (self.OFNSv3))
        for dld in nodes:
            macstr = dld.get("value").strip()
            match.add_dl_dst(macstr)

        nodes = packet_dom.findall('{%s}dl_type' % (self.OFNSv3))
        for dlt in nodes:
            dltstr = dlt.get("value").strip()
            match.add_dl_type(dltstr)

        nodes = packet_dom.findall('{%s}dl_vlan' % (self.OFNSv3))
        for elem in nodes:
            vlidstr = elem.get("value").strip()
            match.add_dl_vlan(vlidstr)

        nodes = packet_dom.findall('{%s}nw_src' % (self.OFNSv3))
        for elem in nodes:
            nwstr = elem.get("value").strip()
            match.add_nw_src(nwstr)

        nodes = packet_dom.findall('{%s}nw_dst' % (self.OFNSv3))
        for elem in nodes:
            nwstr = elem.get("value").strip()
            match.add_nw_dst(nwstr)

        nodes = packet_dom.findall('{%s}nw_proto' % (self.OFNSv3))
        for elem in nodes:
            nwproto = elem.get("value").strip()
            match.add_nw_proto(nwproto)

        nodes = packet_dom.findall('{%s}tp_src' % (self.OFNSv3))
        for elem in nodes:
            tpsrc = elem.get("value").strip()
            match.add_tp_src(tpsrc)

        nodes = packet_dom.findall('{%s}tp_dst' % (self.OFNSv3))
        for elem in nodes:
            tpdst = elem.get("value").strip()
            match.add_tp_dst(tpdst)
            
        return match
            