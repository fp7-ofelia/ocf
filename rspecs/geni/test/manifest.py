import unittest
from geni.v3.container.resource import Resource
from geni.v3.container.sliver import Sliver
from geni.v3.container.slice import Slice
from geni.v3.craftermanager import CrafterRSpecManager
from geni.test.examples import RAW_MANIFEST
from geni.test.examples import FULL_MANIFEST

class ManifestTests(unittest.TestCase):
    
    def setUp(self):
        resources = self.set_up_resources()
        slivers = self.set_up_slivers(resources)
        self.slice = self.set_up_slice(slivers)
        self.manager = CrafterRSpecManager()
        
    def set_up_resources(self):
        resources = list()
        for i in range(0,3):
            resource = Resource()
            resource.set_available(True)
            resource.set_exclusive(True)
            resource.set_urn("urn:publicID:ResourceURN%d" %i)
            resources.append(resource)
            
        return resources
    
    def set_up_slivers(self, resources):
        slivers = list()
        for i in range(0,1):
            sliver = Sliver()
            sliver.set_resources(resources)
            sliver.set_urn("urn:publicID:Sliver%d" % i)
            slivers.append(sliver)
        return slivers
    
    def set_up_slice(self, slivers):
        slicE = Slice()
        slicE.set_component_manager_id("urn:publicID:ComponentManagerID120")
        slicE.set_urn("urn:publicID:SliceName")
        slicE.set_slivers(slivers)
        return slicE
    
    def test_raw_manifest(self):
        self.assertEquals(self.format_rspec(RAW_MANIFEST), self.format_rspec(self.manager.manifest_slice(self.slice)))

    def test_full_manifest(self):
        full_manifest = self.manager.manifest_header()
        full_manifest += self.manager.manifest_slice(self.slice)
        full_manifest += self.manager.manifest_footer()
        self.assertEquals(self.format_rspec(FULL_MANIFEST),self.format_rspec(full_manifest))
        
    def format_rspec(self, string):
        return string.replace(" ", "").replace("\n","")
        
if __name__ == "__main__":
    unittest.main()
    