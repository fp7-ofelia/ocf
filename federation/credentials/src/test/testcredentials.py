import unittest
from credentials.src.test.utils.chcalls import getusercred
from credentials.src.manager.manager import CredentialManager

class TestCredentials(unittest.TestCase):
    
    def setUp(self):
        self.cred = getusercred()[1]['geni_value']
        self.credential_manager = CredentialManager()

    def test_should_check_correct_credential(self):
        print self.credential_manager.validate_for([self.cred], "ListResources")
        
if __name__ == "__main__":
    unittest.main()