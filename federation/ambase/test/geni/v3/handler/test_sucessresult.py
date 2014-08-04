from federation.ambase.src.geni.v3.handler.handler import GeniV3Handler
from federation.ambase.test.utils import testcase


class TestSuccessResult(testcase.TestCase):
    
    def setUp(self):
        self.handler = GeniV3Handler()
        self.message = "This was OK"
        dict1 = {'geni_code':0}
        self.expected = {'code':dict1, 'value': self.message}
    
    def test_should_return_success_result(self):
        self.assertEqual(self.expected, self.handler.success_result(self.message))

if __name__ == "__main__":
    # Allows to run in stand-alone mode
    testcase.main()
