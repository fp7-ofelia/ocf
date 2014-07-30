import unittest
from src.geni.v3.handler.handler import GeniV3Handler
from src.test.utils.mockcredentialmanager import MockCredentialManager
from src.test.utils.mockrspecmanager import MockRSpecManager
from src.test.utils.mockdelegate import MockDelegate
from src.geni.exceptions.manager import GENIExceptionManager
import datetime


class RenewTest(unittest.TestCase):
    ''' Testing Very Basic behaviour to see 
        whether the Handler is able to respond
        with error_results or success_results  
    '''
    
    def setUp(self):
        self.handler = GeniV3Handler()
        self.handler.set_credential_manager(MockCredentialManager())
        self.handler.set_rspec_manager(MockRSpecManager())
        self.handler.set_delegate(MockDelegate())
        self.handler.set_geni_exception_manager(GENIExceptionManager()) #is too simple to mock it
        self.expiration = datetime.datetime.utcnow()
        self.expiration = self.expiration.replace(hour = ((self.expiration.hour + 1) % 24))
        
    def tearDown(self):
        self.handler = None
        
    def test_should_renew(self):
        value = self.handler.Renew([], [], self.expiration, {})
        self.assertEquals(GENIExceptionManager.SUCCESS, value.get('code').get('geni_code'))
    
    def test_should_fail_when_invalid_credentials(self):
        self.handler.set_credential_manager(MockCredentialManager(False))
        value = self.handler.Renew([], [], self.expiration, {})
        self.assertEquals(GENIExceptionManager.FORBIDDEN, value.get('code').get('geni_code'))
    
    def test_should_fail_when_inconsistent_expiration(self):
        self.expiration = datetime.datetime.utcnow()
        self.expiration = self.expiration.replace(year = 2013, month=1, day=1)
        value = self.handler.Renew([], [], self.expiration, {})
        self.assertEquals(GENIExceptionManager.OUTOFRANGE, value.get('code').get('geni_code'))
        
if __name__ == "__main__":
    unittest.main()
        