import sys
sys.path.append("/home/ocf/federation/")
#
# REMOVE PREVIOUS
#
from ambase.src.geni.exceptions.manager import GENIExceptionManager
from ambase.src.geni.v3.handler.handler import GeniV3Handler
from ambase.test.utils import testcase
from ambase.test.utils.mockcredentialmanager import MockCredentialManager
from ambase.test.utils.mockdelegate import MockDelegate
from ambase.test.utils.mockrspecmanager import MockRSpecManager
#from credentials.src.manager.manager import CredentialManager

class TestProvision(testcase.TestCase):
    """ Testing very basic behaviour to see 
        whether the Handler is able to respond
        with error_results or success_results  
    """
    
    def setUp(self):
        self.handler = GeniV3Handler()
        self.handler.set_credential_manager(MockCredentialManager())
        self.handler.set_rspec_manager(MockRSpecManager())
        self.handler.set_delegate(MockDelegate())
        self.handler.set_geni_exception_manager(GENIExceptionManager()) #is too simple to mock it
        self.options = {"geni_rspec_version": {"type": "geni", "version": "3"}}
        self.ret_struct = self.handler.Provision([], [], self.options)
        print "Structure: ", self.ret_struct
        
    def tearDown(self):
        self.handler = None
            
    def test_should_provision(self):
        #print "Slice expiration: ", self.handler.get_credential_manager().get_slice_expiration(None)
        self.assertEquals(GENIExceptionManager.SUCCESS, self.ret_struct("code").get("geni_code"))
    
    def test_shoud_return_error_when_invalid_credentials(self):
        self.handler.set_credential_manager(MockCredentialManager(False))
        self.ret_struct = self.handler.Provision(None, self.options)
        self.assertEquals(GENIExceptionManager.FORBIDDEN, self.ret_struct("code").get("geni_code"))
    
    def test_should_fail_when_no_required_options(self):
        self.assertEquals(GENIExceptionManager.BADARGS, self.ret_struct("code").get("geni_code"))
    
    def test_should_fail_when_provision_error(self):
        self.handler.set_delegate(MockDelegate(False))
        self.ret_struct = self.handler.Provision([], [], self.options)
        self.assertEquals(GENIExceptionManager.ERROR, self.ret_struct("code").get("geni_code"))
    
if __name__ == "__main__":
    # Allows to run in stand-alone mode
    testcase.main()
