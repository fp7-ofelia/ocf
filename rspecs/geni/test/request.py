import unittest
from geni.test.expected_outputs import DEFAULT_AM_OUTPUT
from geni.v3.parsermanager import ParserManager
from geni.test.examples import REQUEST_EXAMPLE

class requestTest(unittest.TestCase):
    
    def setUp(self):
        self.manager = ParserManager()
        self.request = REQUEST_EXAMPLE
        
    def test_should_parse_node(self):
        am = self.manager.parse_request_rspec("MYURN", self.request)
        print "-------",am
        self.assertEquals(DEFAULT_AM_OUTPUT, am)
        
        
        
if __name__== "__main__":
    unittest.main()
        
        
        