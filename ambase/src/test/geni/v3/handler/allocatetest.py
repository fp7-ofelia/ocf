import unittest
from src.geni.v3.handler.handler import GeniV3Handler
from src.test.utils.mockcredentialmanager import MockCredentialManager
from src.test.utils.mockrspecmanager import MockRSpecManager
from src.test.utils.mockdelegate import MockDelegate
from src.geni.exceptions.manager import GENIExceptionManager


class AllocateTest(unittest.TestCase):
    """ Testing very basic behaviour to see 
        whether the Handler is able to respond
        with error_results or success_results  
    """
    
    def setUp(self):
        self.handler = GeniV3Handler()
        self.handler.set_credential_manager(MockCredentialManager())
        self.handler.set_rspec_manager(MockRSpecManager())
        self.handler.set_delegate(MockDelegate())
        self.handler.set_geni_exception_manager(GENIExceptionManager()) # Too simple to mock
    
    def tearDown(self):
        self.handler = None
    
    def test_should_allocate(self):
        value = self.handler.Allocate(None, None, None, {})
        self.assertEquals(GENIExceptionManager.SUCCESS, value.get('code').get('geni_code'))
    
    def test_should_fail_when_invalid_credentials(self):
        self.handler.set_credential_manager(MockCredentialManager(False))
        value = self.handler.Allocate(None, None, None, {})
        self.assertEquals(GENIExceptionManager.FORBIDDEN, value.get('code').get('geni_code'))
    
    def test_should_catch_already_exist_error(self):
        self.handler.set_delegate(MockDelegate(True,True))
        value = self.handler.Allocate(None,None,None, {})
        self.assertEquals(GENIExceptionManager.ALREADYEXISTS, value.get('code').get('geni_code'))
    
    def test_should_catch_allocation_error(self):
        self.handler.set_delegate(MockDelegate(False,False))
        value = self.handler.Allocate()
        self.assertEquals(GENIExceptionManager.ERROR, value.get('code').get('geni_code'))
