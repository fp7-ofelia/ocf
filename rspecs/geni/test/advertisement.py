import unittest
from geni.v3.container.resource import Resource
from geni.v3.craftermanager import CrafterRSpecManager
from geni.test.examples import RAW_NODES
from geni.test.examples import AD_RSPEC

class advertisementTest(unittest.TestCase):
    
    def setUp(self):
        self.resources = self.get_default_resources()
        self.manager = CrafterRSpecManager()
        
    def tearDown(self):
        self.resources = []
        
    def get_default_resources(self):
        resources = list()
        for i in range(0,4):
            r = Resource()
            r.set_id(i)
            r.set_exclusive(True)
            r.set_urn("urn:publicID:ThisisaURNof%d" %i)
            resources.append(r)
        return resources
    
    def test_shouldAdvertiseNodes(self):
        string = ""
        for r in self.resources:
            adv = self.manager.advert_resource(r)
            string += adv
        self.assertEquals(self.format_rspec(RAW_NODES), self.format_rspec(string))
        
    def test_shouldAdvertiseFullRSpec(self):
        string = self.manager.advert_header()
        for r in self.resources:
            string += self.manager.advert_resource(r)
        string += self.manager.advert_footer()
        self.assertEquals(self.format_rspec(AD_RSPEC), self.format_rspec(string))
        
        
    def format_rspec(self, string):
        return string.replace(" ", "").replace("\n","")
  
if __name__ == "__main__":
    unittest.main()
