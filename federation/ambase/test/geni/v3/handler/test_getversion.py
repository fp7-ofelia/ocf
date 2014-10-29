from ambase.src.geni.exceptions.manager import GENIExceptionManager
from ambase.src.geni.v3.handler.handler import GeniV3Handler
from ambase.test.utils import testcase
from ambase.test.utils.mockcredentialmanager import MockCredentialManager
from ambase.test.utils.mockdelegate import MockDelegate
from ambase.test.utils.mockrspecmanager import MockRSpecManager
from ambase.src.geni.v3.delegate.delegate import GeniV3Delegate

class TestGetVersion(testcase.TestCase):
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
        self.handler.set_geni_exception_manager(GENIExceptionManager()) # Too simple to mock
        self.ret_struct = self.handler.GetVersion({})
        print self.ret_struct

    
    def tearDown(self):
        self.handler = None
        
    def test_should_get_version(self):
        self.assertEquals(GENIExceptionManager.SUCCESS, self.ret_struct.get("code").get("geni_code"))
        
    def test_should_send_error_result_when_error(self):
        self.handler.set_delegate(MockDelegate(False))
        self.ret_struct = self.handler.GetVersion({})
        self.assertEquals(GENIExceptionManager.ERROR, self.ret_struct.get("code").get("geni_code"))
        
    def test_should_return_get_version_of_real_Delegate(self):
        self.handler.set_delegate(GeniV3Delegate())
        print self.handler.GetVersion()
        

    
if __name__ == "__main__":
    # Allows to run in stand-alone mode
    testcase.main()
