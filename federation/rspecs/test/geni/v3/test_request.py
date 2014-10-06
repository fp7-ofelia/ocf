from rspecs.src.geni.v3.parsermanager import ParserManager
from rspecs.test.geni.v3.examples import REQUEST_EXAMPLE
from rspecs.test.utils import testcase
from rspecs.test.geni.v3.expected_outputs import DEFAULT_AM_OUTPUT


class TestRequest(testcase.TestCase):
    
    def setUp(self):
        self.manager = ParserManager()
        self.request = REQUEST_EXAMPLE
        
    def test_should_parse_node(self):
        req = self.manager.parse_request_rspec(self.request)
        self.assertEquals(DEFAULT_AM_OUTPUT, str(req))
    
if __name__ == '__main__':
    testcase.main()
