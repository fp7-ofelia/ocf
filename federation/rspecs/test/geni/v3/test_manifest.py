from rspecs.src.geni.v3.container.resource import Resource
from rspecs.src.geni.v3.container.sliver import Sliver
from rspecs.src.geni.v3.craftermanager import CrafterManager
from rspecs.test.geni.v3.examples import RAW_MANIFEST
from rspecs.test.geni.v3.examples import FULL_MANIFEST
from rspecs.test.utils import testcase


class TestManifest(testcase.TestCase):
    
    def setUp(self):
        self.resources = self.set_up_resources()
        self.manager = CrafterManager()
        
    def set_up_resources(self):
        resources = list()
        for i in range(0,3):
            resource = Resource()
            resource.set_id(i)
            resource.set_available(True)
            resource.set_exclusive(True)
            resource.set_component_manager_id("urn:publicID:ResourceURN%d" %i)
            resource.set_component_manager_name("urn:publicID:ResourceURN%d" %i)
            resource.set_component_id("urn:publicID:ResourceURN%d" %i)
            resource.set_component_name("urn:publicID:ResourceURN%d" %i)
            resource.set_sliver(self.set_up_sliver(resource))
            resources.append(resource)
        return resources
    
    def set_up_sliver(self, resource):
        sliver = Sliver()
        sliver.set_resource(resource)
        sliver.set_urn("urn:publicID:Sliver%d" %resource.get_id())
        return sliver
    
    def test_raw_manifest(self):
        self.assertEquals(self.format_rspec(RAW_MANIFEST), self.format_rspec(self.manager.manifest_slivers(self.resources)))
    
    def test_full_manifest(self):
        full_manifest = self.manager.manifest_header()
        full_manifest += self.manager.manifest_slivers(self.resources)
        full_manifest += self.manager.manifest_footer()
        self.assertEquals(self.format_rspec(FULL_MANIFEST),self.format_rspec(full_manifest))
    
    def format_rspec(self, string):
        return string.replace(" ", "").replace("\n","")
    
if __name__ == '__main__':
    # Allows to run in stand-alone mode
    testcase.main()
