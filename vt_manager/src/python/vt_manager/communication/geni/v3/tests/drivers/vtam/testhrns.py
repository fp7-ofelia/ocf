import sys
sys.path.append("/opt/ofelia/core/lib/am/")
sys.path.append("/opt/ofelia/core/lib/")

import unittest
from am.geniutils.src.xrn.xrn import urn_to_hrn
from am.geniutils.src.xrn.xrn import hrn_to_urn

class TestHRNs(unittest.TestCase):
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
        self.component_urn_template = "urn:publicid:IDN+ocf:i2cat:vtam+authority+cm"
        
        self.authority_type = "authority"
        self.component_type = "authority+cm"
        self.node_type = "node"
        self.slice_type = "slice"
        self.sliver_type ="sliver"
        
        self.authority_hrn = "ocf.i2cat"
        self.component_hrn = "ocf.i2cat.vtam"
        self.node_hrn = 'ocf.i2cat.vtam.Foix'
        self.slice_hrn = 'ocf.i2cat.vtam.mytestslice'
        self.sliver_hrn = 'ocf.i2cat.vtam.123' 

    def test_should_get_hrn_authority(self):
        authority_urn = hrn_to_urn(self.authority_hrn, self.authority_type)
        self.assertEquals(self.authority_urn_template, authority_urn)

    def test_should_get_hrn_slice(self):
        slice_urn = hrn_to_urn(self.slice_hrn, self.slice_type)
        self.assertEquals(self.slice_urn_template, slice_urn)

    def test_should_get_hrn_sliver(self):
        sliver_urn = hrn_to_urn(self.sliver_hrn, self.sliver_type)
        self.assertEquals(self.sliver_urn_template, sliver_urn)

    def test_should_get_hrn_node(self):
        node_urn = hrn_to_urn(self.node_hrn, self.node_type)
        self.assertEquals(self.node_urn_template, node_urn)

    def test_should_get_hrn_component_manager(self):
        component_urn = hrn_to_urn(self.component_hrn, self.component_type)
        self.assertEquals(self.component_urn_template, component_urn)
   
if __name__ == "__main__":
    unittest.main()
