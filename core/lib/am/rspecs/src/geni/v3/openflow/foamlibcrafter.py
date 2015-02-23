# Copyright (c) 2011-2012  The Board of Trustees of The Leland Stanford Junior University

from cStringIO import StringIO
from lxml import etree as ET


class FOAMLibCrafter:
    
    def __init__(self):
    
        self.OFNSv3 = "http://www.geni.net/resources/rspec/ext/openflow/3"
        self.OFNSv4 = "http://www.geni.net/resources/rspec/ext/openflow/4"
        #TOPONSv1 = "http://geni.bssoftworks.com/rspec/ext/topo/1"
        self.PGNS = "http://www.geni.net/resources/rspec/3"
        self.XSNS = "http://www.w3.org/2001/XMLSchema-instance"
        self.__config = None
        
    def get_config(self):
        return self.__config
    
    def set_config(self, value):
        self.__config = value
    
    def get_advertisement(self, resources):
        NSMAP = {None: "%s" % (self.PGNS),
                       "xs" : "%s" % (self.XSNS),
                       "openflow" : "%s" % (self.OFNSv3)}

        rspec = ET.Element("rspec", nsmap=NSMAP)
        rspec.attrib["{%s}schemaLocation" % (self.XSNS)] = self.PGNS + " " \
                     "http://www.geni.net/resources/rspec/3/ad.xsd " + \
                     self.OFNSv3 + " " \
                     "http://www.geni.net/resources/rspec/ext/openflow/3/of-ad.xsd"
        rspec.attrib["type"] = "advertisement"
        
        links = self.filter_links(resources)
        devices = self.filter_devices(resources)

        for dpid in devices:
            self.ad_device(rspec, dpid)
 
        for link in links:
            self.ad_link(rspec, link)

        xml = StringIO()
        ET.ElementTree(rspec).write(xml)
        return xml.getvalue()
    

    #def generateSwitchComponentID(self, dpid):
    #    return "urn:publicid:IDN+openflow:%s+datapath+%s" % (config.HRN, dpid.get_datapath())
    
    
    def ad_device (self, rspec, dpid, active=True):
        od = ET.SubElement(rspec, "{%s}datapath" % (self.OFNSv3))
        od.attrib["component_id"] = dpid.get_component_id()
        od.attrib["component_manager_id"] = dpid.get_component_manager_id()
        od.attrib["dpid"] = str(dpid.get_datapath())

        locdata = None
        if locdata:
            ET.SubElement(od, "{%s}location" % (self.OFNSv3), country=locdata.country, latitude=locdata.lat, longitude=locdata.long)

        if active:
            ports = dpid.get_ports()
            for port in ports:
                if (port.get_features() == None):
                    p = ET.SubElement(od, "{%s}port" % (self.OFNSv3), num=str(port.get_num()), name=str(port.get_name()))
                else:
                    p = ET.SubElement(od, "{%s}port" % (self.OFNSv3), num=str(port.get_num()), name=str(port.get_name()), features=port.get_features())
                #for info in attachments.setdefault(port.name, []):
                #    a = ET.SubElement(p, "{%s}attachment" % (self.OFNSv3))
                #    a.attrib["remote_component_id"] = info.remote_component_id
                #    a.attrib["remote_port"] = info.remote_port
                #    a.attrib["desc"] = info.desc
        
    def ad_link(self, rspec, link, federated=False):
  
        def add_dpid(od, datapath):
            dpids = ET.SubElement(od, "{%s}datapath" %(self.OFNSv3))
            dpids.attrib["component_id"] = datapath.get_component_id()#"urn:publicid:IDN+openflow:%s+datapath+%s" % (config.HRN, str(datapath))
            dpids.attrib["component_manager_id"] = datapath.get_component_manager_id()#"urn:publicid:IDN+openflow:%s+cm" % (config.HRN)
            dpids.attrib["dpid"] = str(datapath.get_datapath())
                
        def add_port(od, port):
            ps = ET.SubElement(od, "{%s}port" %(self.OFNSv3))
            ps.attrib["port_num"] = str(port)
                
        def add_device(od, device):
            devices = ET.SubElement(od, "{%s}device" %(self.OFNSv3))
            devices.attrib["component_id"] = device.get_component_id() #"urn:publicid:IDN+federation:%s+device+%s" % (config.HRN, device)
            devices.attrib["component_manager_id"] = device.get_component_manager_id()#"urn:publicid:IDN+federation:%s+cm" % (config.HRN)
                
        if federated:
            add = add_device
        else:
            add = add_dpid
 
        od = ET.SubElement(rspec, "{%s}link" % (self.OFNSv3))
        od.attrib["component_id"] = link.get_component_id()#"urn:publicid:IDN+openflow:%s+link+%s_%s_%s_%s" %(config.HRN,str(link.get_src_dpid().get_datapath()), str(link.get_src_port().get_num()),str(link.get_dst_dpid().get_datapath()),str(link.get_dst_port().get_num()))
        add(od, link.get_src_dpid())
        add_port(od, link.get_src_port().get_num())
        add(od,link.get_dst_dpid())
        add_port(od,link.get_dst_port().get_num()) 
        
    def get_manifest(self, flowspace):
        NSMAP = {None: "%s" % (self.PGNS),
                       "xs" : "%s" % (self.XSNS),
                       "openflow" : "%s" % (self.OFNSv3)}

        rspec = ET.Element("rspec", nsmap=NSMAP)
        rspec.attrib["{%s}schemaLocation" % (self.XSNS)] = self.PGNS + " " \
                     "http://www.geni.net/resources/rspec/3/manifest.xsd " + \
                     self.OFNSv3 + " " \
                     "http://www.geni.net/resources/rspec/ext/openflow/3/of-resv.xsd"
        rspec.attrib["type"] = "manifest"
        
        od = ET.SubElement(rspec, "{%s}sliver" % (self.OFNSv3))
        od.attrib["urn"] = flowspace.get_urn()
        od.attrib["description"] = flowspace.get_urn()
        od.attrib["email"] = flowspace.get_email()
        od.attrib["status"] =  flowspace.get_state()
        
        xml = StringIO()
        ET.ElementTree(rspec).write(xml)
        return xml.getvalue() 
        
    def filter_links(self, resources):
        return self.__filter_by("Link", resources)
        
    def filter_devices(self, resources):
        return self.__filter_by("Device", resources)
       
        
    def __filter_by(self, filter_key, resources ):
            filtered_resources = list()        
            for r in resources:
                if r.get_type() == filter_key:
                    filtered_resources.append(r)
            return filtered_resources        
                      
