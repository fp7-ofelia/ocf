import unittest
from rspecs.src.geni.v3.openflow.foamlibcrafter import FOAMLibCrafter
from rspecs.src.geni.v3.openflow.container.dpid import DPID
from rspecs.src.geni.v3.openflow.container.port import Port
from rspecs.src.geni.v3.openflow.container.link import Link
from rspecs.test.geni.v3.openflow.expectedoutputs import EXPECTED_AD_RSPEC
from settings.src.settings import Settings as config


class TestAdvertisement(unittest.TestCase):
    
    def setUp(self):
        self.resources = self.get_test_resources()
        self.rspec_crafter = FOAMLibCrafter()
        self.advertisement_rspec = self.rspec_crafter.get_advertisement(self.resources)
        
    def test_should_advertise_OF_resources(self):
        self.assertEquals(self.format_rspec(EXPECTED_AD_RSPEC), self.format_rspec(self.advertisement_rspec))    

    def get_test_resources(self):
        resources = list()
        old_dpid = self.create_dpid(0)
        resources.append(old_dpid)
        for i in range(1,5):
            dpid = self.create_dpid(i)
            link = self.create_link(old_dpid, dpid)
            resources.append(dpid)
            resources.append(link)
            old_dpid = dpid
            
        return resources 
    
    def create_dpid(self, id):
        dpid = DPID()
        dpid.set_type("Device")
        dpid.set_datapath(id)
        dpid.set_component_id("urn:publicid:IDN+openflow:%s+datapath+%s" % (config.HRN, dpid.get_datapath()))
        dpid.set_component_manager_id("urn:publicid:IDN+openflow:%s+authorithy+cm" % (config.HRN))
        for i in range(1,4):
            port = Port()
            port.set_name(i)
            port.set_num(i)
            dpid.add_port(port)
        return dpid
    
    def create_link(self, old_dpid, dpid):
        link = Link()
        link.set_type("Link")
        link.set_src_dpid(old_dpid)
        link.set_src_port(old_dpid.get_ports()[0])
        link.set_dst_dpid(dpid)
        link.set_dst_port(dpid.get_ports()[0])
        link.set_component_id("urn:publicid:IDN+openflow:%s+link+%s_%s_%s_%s" %(config.HRN,str(link.get_src_dpid().get_datapath()), str(link.get_src_port().get_num()),str(link.get_dst_dpid().get_datapath()),str(link.get_dst_port().get_num())))
        
        return link
    
    def format_rspec(self, string):
        return string.replace(" ", "")
