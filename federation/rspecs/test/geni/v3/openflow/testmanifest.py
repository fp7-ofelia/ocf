import unittest
from rspecs.src.geni.v3.openflow.foamlibcrafter import FOAMLibCrafter
from rspecs.src.geni.v3.openflow.container.flowspace import FlowSpace
from rspecs.test.geni.v3.openflow.expectedoutputs import EXPECTED_MAN_RSPEC

class TestManaifest(unittest.TestCase):
    
    def setUp(self):
        self.crafter = FOAMLibCrafter()
        self.flowspace = self.get_flowspace()
        self.manifest = self.crafter.get_manifest(self.flowspace)
        
    def get_flowspace(self):
        flowspace = FlowSpace()
        flowspace.set_state("Pending of approval")
        flowspace.set_description("Test slice")
        flowspace.set_urn("urn:publicID:myTest:openflow:manfifest+slice")
        flowspace.set_email("john@doe.doe")
        return flowspace
    
    def test_should_manifest(self):
        self.assertEquals(EXPECTED_MAN_RSPEC, self.manifest)
           
if __name__ == "__main__":
    unittest.TestCase()