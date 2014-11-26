import sys
sys.path.append("/opt/ofelia/core/lib/am/")
sys.path.append("/opt/ofelia/core/lib/")

import unittest
from am.geniutils.src.xrn.xrn import urn_to_hrn
from am.geniutils.src.xrn.xrn import hrn_to_urn

class TestURNs(unittest.TestCase):
    '''Test devoted to find URN Parsers, 
       USEFUL INFO
       ----------- 
       slice_urn_format: urn:publicid:IDN+<SA name>+slice+<slice name>
       sliver_urn_format: urn:publicid:IDN+<AM name>+sliver+<sliver name>
       node_urn_format: urn:publicid:IDN+<AM name>+node+<node name>
    '''
    
    def setUp(self):
        self.authority_urn_template = "urn:publicid:IDN+ocf:i2cat+authority+sa"
        self.slice_urn_template = "urn:publicid:IDN+ocf:i2cat:vtam+slice+mytestslice"
        self.node_urn_template =  "urn:publicid:IDN+ocf:i2cat:vtam+node+Foix"
        self.sliver_urn_template = "urn:publicid:IDN+ocf:i2cat:vtam+sliver+123"
        self.component_manager_urn_template = "urn:publicid:IDN+ocf:i2cat:vtam+authority+cm"
        
        self.authority_type = "authority"
        self.node_type = "node"
        self.slice_type = "slice"
        self.sliver_type ="sliver"
        
        self.authority_hrn = "ocf.i2cat"
        self.node_hrn = 'ocf.i2cat.vtam.Foix'
        self.slice_hrn = 'ocf.i2cat.vtam.mytestslice'
        self.sliver_hrn = 'ocf.i2cat.vtam.123' 

    def test_should_get_hrn_authority(self):
        authority_hrn, hrn_type = urn_to_hrn(self.authority_urn_template)
        self.assertEquals(self.authority_hrn, authority_hrn)
        self.assertEquals(self.authority_type, hrn_type)

    def test_should_get_hrn_slice(self):
        slice_hrn, hrn_type = urn_to_hrn(self.slice_urn_template)
        self.assertEquals(self.slice_hrn, slice_hrn)
        self.assertEquals(self.slice_type, hrn_type)

    def test_should_get_hrn_sliver(self):
        sliver_hrn, hrn_type = urn_to_hrn(self.sliver_urn_template)
        self.assertEquals(self.sliver_hrn, sliver_hrn)
        self.assertEquals(self.sliver_type, hrn_type)

    def test_should_get_hrn_node(self):
        node_hrn, hrn_type = urn_to_hrn(self.node_urn_template)
        self.assertEquals(self.node_hrn, node_hrn)
        self.assertEquals(self.node_type, hrn_type)

    def test_should_get_hrn_component_manager(self):
        cm_hrn, hrn_type = urn_to_hrn(self.component_manager_urn_template)
        print cm_hrn, hrn_type

if __name__ == "__main__":
    unittest.main()
