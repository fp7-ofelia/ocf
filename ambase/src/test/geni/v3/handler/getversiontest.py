import unittest
from src.geni.v3.handler.handler import GeniV3Handler
from src.test.utils.mockcredentialmanager import MockCredentialManager
from src.test.utils.mockrspecmanager import MockRSpecManager
from src.test.utils.mockdelegate import MockDelegate
from src.geni.exceptions.manager import GENIExceptionManager


class GetVersionTest(unittest.TestCase):
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
        
    def test_should_get_version(self):
        # TODO
        value = self.handler.GetVersion({})
        print value
        self.assertEquals(GENIExceptionManager.SUCCESS, value.get('code').get('geni_code'))
    
    def should_respond_all_get_version_fields(self):
        pass
    
    def test_should_send_correctly_formatted_output(self):
        # TODO
        self.handler.set_delegate(MockDelegate(True))
        value = self.handler.GetVersion({})
        self.assertEquals(GENIExceptionManager.SUCCESS, value.get('code').get('geni_code'))
