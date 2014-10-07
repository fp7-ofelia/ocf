import unittest
from rspecs.src.geni.v3.openflow.foamlibparser import FOAMLibParser
from rspecs.test.geni.v3.openflow.requestexamples import FULL_REQUEST

class TestRequest(unittest.TestCase):
    
    def setUp(self):
        self.request_rspec = FULL_REQUEST
        self.parser = FOAMLibParser()
        self.flowspace = self.parser.parse_request(FULL_REQUEST)
        self.controller = self.flowspace.get_controller()
        self.groups = self.flowspace.get_groups()
        self.dpids = self.groups[0].get_dpids()
        self.ports = self.dpids[0].get_ports()
        self.matches = self.groups[0].get_matches()
         
    def test_should_parse_request(self):
        print self.flowspace
        
    def test_dpids_should_be_parsed(self):
        self.assertEquals(2, len(self.dpids))

    def test_ports_should_be_parsed(self):
        self.assertEquals(2, len(self.ports))
        
    def test_controller_should_be_parsed(self):
        self.assertTrue(self.controller is not None)
        
    def test_flowspace_match_should_parsed(self):
        self.assertEquals(2, len(self.matches))
             
if __name__ == "__main__":
    unittest.main()
        