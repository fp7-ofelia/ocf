from rspecs.src.geni.v3.container.resource import Resource
from rspecs.src.geni.v3.craftermanager import CrafterManager
from rspecs.test.utils import testcase
from rspecs.test.geni.v3.examples import RAW_NODES
from rspecs.test.geni.v3.examples import AD_RSPEC

class TestAdvertisement(testcase.TestCase):
    
    def setUp(self):
        self.resources = self.get_default_resources()
        self.manager = CrafterManager()
        
    def tearDown(self):
        self.resources = []
        
    def get_default_resources(self):
        resources = list()
        for i in range(0,4):
            r = Resource()
            r.set_id(i)
            r.set_exclusive(True)
            r.set_component_id("urn:publicID:ThisisaURNof%d" %i)
            r.set_component_manager_id("urn:publicID:ThisisaURNof%d" %i)
            r.set_component_name("urn:publicID:ThisisaURNof%d" %i)
            r.set_component_manager_name("urn:publicID:ThisisaURNof%d" %i)
            resources.append(r)
        return resources
    
    def format_rspec(self, string):
        return string.replace(" ", "").replace("\n","")
    
    def test_should_advertise_nodes(self):
        string = ""
        for r in self.resources:
            adv = self.manager.advert_resource(r)
            string += adv     
        self.assertEquals(self.format_rspec(RAW_NODES), self.format_rspec(string))
        
    def test_should_advertise_full_rspec(self):
        string = self.manager.advert_header()
        for r in self.resources:
            string += self.manager.advert_resource(r)
        string += self.manager.advert_footer()
        print self.format_rspec(string)
        self.assertEquals(self.format_rspec(AD_RSPEC), self.format_rspec(string))
    
if __name__ == '__main__':
    # Allows to run in stand-alone mode
    testcase.main()
