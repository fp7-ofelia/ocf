from ambase.src.geni.exceptions.manager import GENIExceptionManager
from ambase.src.geni.v3.handler.handler import GeniV3Handler
from ambase.test.utils import testcase
from ambase.test.utils.mockcredentialmanager import MockCredentialManager
from ambase.test.utils.mockdelegate import MockDelegate
from ambase.test.utils.mockrspecmanager import MockRSpecManager

class TestShutdown(testcase.TestCase):
    """
        Testing very basic behaviour to see 
        whether the Handler is able to respond
        with error_results or success_results  
    """
    
    def setUp(self):
        self.handler = GeniV3Handler()
        self.handler.set_credential_manager(MockCredentialManager())
        self.handler.set_rspec_manager(MockRSpecManager())
        self.handler.set_delegate(MockDelegate())
        self.handler.set_geni_exception_manager(GENIExceptionManager()) #is too simple to mock it
        
    def tearDown(self):
        self.handler = None
        
    def test_should_fail_always(self):
        self.ret_struct = self.handler.Shutdown()
        self.assertEquals(GENIExceptionManager.FORBIDDEN, self.ret_struct.get("code").get("geni_code"))
    
if __name__ == "__main__":
    # Allows to run in stand-alone mode
    testcase.main()