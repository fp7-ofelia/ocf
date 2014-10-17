from ambase.src.geni.exceptions.manager import GENIExceptionManager
from ambase.src.geni.v3.handler.handler import GeniV3Handler
from ambase.test.utils.mockcredentialmanager import MockCredentialManager
from ambase.test.utils.mockdelegate import MockDelegate
from ambase.test.utils.mockrspecmanager import MockRSpecManager
import unittest


class TestPerformOperationalAction(unittest.TestCase):
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
        # XXX Add incorrect credentials for the second parameter
        value = self.handler.PerformOperationalAction([], None, "geni_start", {})
        self.assertEquals(GENIExceptionManager.FORBIDDEN, value.get('code').get('geni_code'))
    
    def test_should_return_correct_value_structure(self):
        value = self.handler.PerformOperationalAction([], [], "geni_start", {}) 
        obtained = value.get("value")
        obtained.sort()
        self.assertTrue(type(obtained) == list)
        
    def test_should_return_correct_sliver_value_structure(self):
        value = self.handler.PerformOperationalAction([], [], "geni_start", {})
        struct = self.get_geni_slivers_content()[0].keys()
        struct.sort()
        obtained = value.get("value")[0].keys()
        obtained.sort()
        self.assertEquals(struct, obtained)    
        
    def get_expected_return_structure(self):
        struct = {"geni_rspec" : "None",
                  "geni_slivers" : [],}
        return struct
    
    def get_geni_slivers_content(self):
        return [{ "geni_sliver_urn": "urn",
                  "geni_allocation_status": "string",
                  "geni_operational_status":"String",
                  "geni_expires":"String"}]
    
if __name__ == "__main__":
    # Allows to run in stand-alone mode
    unittest.main()
