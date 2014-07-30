import unittest
from src.geni.v3.handler.handler import GeniV3Handler
from src.test.utils.mockcredentialmanager import MockCredentialManager
from src.test.utils.mockrspecmanager import MockRSpecManager
from src.test.utils.mockdelegate import MockDelegate
from src.geni.exceptions.manager import GENIExceptionManager


class PerformOperationalActionTest(unittest.TestCase):
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
        
    def tearDown(self):
        self.handler = None
        
    def test_should_perform_operational_action_start(self):
        value = self.handler.PerformOperationalAction([], [], "geni_start", {})
        self.assertEquals(GENIExceptionManager.SUCCESS, value.get('code').get('geni_code'))
    
    def test_should_perform_operational_action_stop(self):
        value = self.handler.PerformOperationalAction([], [], "geni_stop", {})
        self.assertEquals(GENIExceptionManager.SUCCESS, value.get('code').get('geni_code'))
        
    def test_should_perform_operational_action_restart(self):
        value = self.handler.PerformOperationalAction([], [], "geni_restart", {})
        self.assertEquals(GENIExceptionManager.SUCCESS, value.get('code').get('geni_code'))
    
    def test_should_fail_when_invalid_action(self):
        value = self.handler.PerformOperationalAction([], [], "do_something", {})
        self.assertEquals(GENIExceptionManager.UNSUPPORTED, value.get('code').get('geni_code'))
        
    def test_should_fail_when_inconsistent_action(self):
        self.handler.set_delegate(MockDelegate(False))
        value = self.handler.PerformOperationalAction([], [], "geni_start", {})
        self.assertEquals(GENIExceptionManager.BADARGS, value.get('code').get('geni_code'))

    def test_shoud_return_error_when_invalid_credentials(self):
        self.handler.set_credential_manager(MockCredentialManager(False))
        value = self.handler.PerformOperationalAction(None, self.options)
        self.assertEquals(GENIExceptionManager.FORBIDDEN, value.get('code').get('geni_code'))
    
if __name__ == "__main__":
    unittest.main()
    
    
        