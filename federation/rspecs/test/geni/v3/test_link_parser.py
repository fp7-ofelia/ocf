from rspecs.src.geni.v3.parsermanager import ParserManager
from rspecs.test.geni.v3.examples import LINK_REQUEST
from rspecs.test.utils import testcase
from rspecs.test.geni.v3.expected_outputs import DEFAULT_LINK_OUTPUT

class TestLinkParser(testcase.TestCase):
    
    def setUp(self):
        self.manager = ParserManager()
        self.request = LINK_REQUEST
        
    def test_should_parse_node(self):
        req = self.manager.parse_request_rspec(self.request)
        self.assertEquals(DEFAULT_LINK_OUTPUT, str(req))
    
if __name__ == '__main__':
    testcase.main()