from ambase.src.geni.exceptions.manager import GENIExceptionManager
from ambase.src.geni.v3.handler.handler import GeniV3Handler
from ambase.test.utils import testcase
from ambase.test.utils.mockcredentialmanager import MockCredentialManager
from ambase.test.utils.mockdelegate import MockDelegate
from ambase.test.utils.mockrspecmanager import MockRSpecManager
import datetime
import dateutil.parser

class TestRenew(testcase.TestCase):
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
        self.expiration = datetime.datetime.utcnow()
        # Requested expiration is 10 minutes (less than default 1 hour)
        self.expiration = self.expiration + datetime.timedelta(minutes = 10)
        self.ret_struct = self.handler.Renew([], [], self.expiration, {})
        
    def tearDown(self):
        self.handler = None
        
    def test_should_renew(self):
        self.assertEquals(GENIExceptionManager.SUCCESS, self.ret_struct.get("code").get("geni_code"))
    
    def test_should_fail_when_invalid_credentials(self):
        self.handler.set_credential_manager(MockCredentialManager(False))
        self.ret_struct = self.handler.Renew([], [], self.expiration, {})
        self.assertEquals(GENIExceptionManager.FORBIDDEN, self.ret_struct.get("code").get("geni_code"))
    
    def test_should_fail_when_requested_expiration_more_than_slice_expiration(self):
        self.expiration = datetime.datetime.utcnow()
        self.expiration = self.expiration.replace(year = self.expiration.year+1000)
        self.expiration = self.expiration.replace(tzinfo=dateutil.tz.tzutc()).strftime("%Y-%m-%d %H:%M:%S").replace(" ", "T")+"Z"
        self.ret_struct = self.handler.Renew([], [], self.expiration, {})
        self.assertEquals(GENIExceptionManager.EXPIRED, self.ret_struct.get("code").get("geni_code"))
    
    def test_should_fail_when_requested_expiration_less_than_current_time(self):
        self.expiration = datetime.datetime.utcnow()
        self.expiration = self.expiration.replace(hour=((self.expiration.hour-1)%24))
        self.expiration = self.expiration.replace(tzinfo=dateutil.tz.tzutc()).strftime("%Y-%m-%d %H:%M:%S").replace(" ", "T")+"Z"
        self.ret_struct = self.handler.Renew([], [], self.expiration, {})
        self.assertEquals(GENIExceptionManager.ERROR, self.ret_struct.get("code").get("geni_code"))
    
    def get_expected_return_structure(self):
        return {
                    "geni_sliver_urn" : str,
                    "geni_allocation_status" : str,
                    "geni_operational_status": str,
                    "geni_expires": str,
                }
    
    def test_should_return_correct_keys(self):
        required_keys = self.get_expected_return_structure().keys()
        required_keys.sort()
        for struct in self.ret_struct.get("value"):
            obtained_keys = struct.keys()
            obtained_keys.sort()
            self.assertEquals(required_keys, obtained_keys)
   
    def test_should_return_list_of_slivers(self):
        self.assertEquals(list, type(self.ret_struct.get("value")))
     
    def test_should_return_correct_values(self):
        required_keys = self.get_expected_return_structure().keys()
        required_keys.sort()
        required_types = [ self.get_expected_return_structure().get(k) for k in required_keys ]
        required_types.sort()
        # NOTE: this implies that "value" contains a list
        for struct in self.ret_struct.get("value"):
            obtained_keys = struct.keys()
            obtained_keys.sort()
            obtained_types = [ type(struct.get(k)) for k in obtained_keys ]
            obtained_types.sort()
            self.assertEquals(required_types, obtained_types)
    
if __name__ == "__main__":
    # Allows to run in stand-alone mode
    testcase.main()
