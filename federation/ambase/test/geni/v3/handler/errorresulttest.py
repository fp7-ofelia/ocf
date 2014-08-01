from federation.ambase.src.geni.v3.handler.handler import GeniV3Handler
import unittest


class ErrorResultTest(unittest.TestCase):

    def setUp(self):
        self.handler = GeniV3Handler()
        self.message = "This was NOT OK"
        self.code = 999
        dict1 = {'geni_code':self.code}
        self.expected = {'code':dict1, 'output': self.message}
             
    def test_should_return_success_result(self):
        self.assertEqual(self.expected, self.handler.error_result(self.code, self.message))
        
if __name__ == "__main__":
    unittest.main()