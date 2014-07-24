import unittest
from src.geni.v3.handler.handler import GeniV3Handler
from src.test.utils.mockcredentialmanager import MockCredentialManager
from src.test.utils.mockrspecmanager import MockRSpecManager
from src.test.utils.mockdelegate import MockDelegate
from src.geni.exceptions.manager import GENIExceptionManager


class AllocateTest(unittest.TestCase):
    ''' Testing Very Basic behaviour to see 
        whether the Handler is able to respond
        with error_results or success_results  
    '''
    
    def setUp(self):
        self.handler = GeniV3Handler()
        self.handler.set_credential_manager(MockCredentialManager)
        self.handler.set_rspec_manager(MockRSpecManager)
        self.handler.set_delegate(MockDelegate)
        self.handler.set_geni_exception_manager(GENIExceptionManager) #is too simple to mock it
        
    def tearDown(self):
        self.handler = None
        
    def test_should_allocate(self):
        pass
    
    def test_should_fail_when_invalid_credentials(self):
        pass
    
    def should_catch_already_exist_error(self):
        pass
    
    def should_catch_allocation_error(self):
        pass
    
    def should_send_responses_correctly_formatted(self):
        pass
    
    def should_respond_error_when_error(self):
        pass
    
