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

import datetime
import dateutil.parser

class TestAllocate(testcase.TestCase):
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
        self.ret_struct = self.handler.Allocate(None, None, None, {})
    
    def tearDown(self):
        self.handler = None
    
    def test_should_allocate_successfully(self):
        self.assertEquals(GENIExceptionManager.SUCCESS, self.ret_struct.get("code").get("geni_code"))
    
    def test_should_allocate_with_sooner_user_expiration(self):
        current_time = datetime.datetime.utcnow()
        # User expiration time: 10 minutes from now (far less than the default 60 minutes)
        user_expiration_time = current_time + datetime.timedelta(minutes = 10)
        user_expiration_time = user_expiration_time.replace(tzinfo=dateutil.tz.tzutc()).strftime("%Y-%m-%d %H:%M:%S")
        user_expiration_time = user_expiration_time.replace(" ", "T")+"Z"
        self.ret_struct = self.handler.Allocate(None, None, None, {"geni_end_time": user_expiration_time})
        self.assertEquals(user_expiration_time, self.ret_struct.get("value").get("geni_slivers")[0].get("geni_expires"))
    
    def test_should_fail_with_later_user_expiration(self):

        current_time = datetime.datetime.utcnow()
        # User expiration time: 1 day from now (far more than the default 60 minutes)
        user_expiration_time = current_time + datetime.timedelta(days = 1)
        user_expiration_time = user_expiration_time.replace(tzinfo=dateutil.tz.tzutc()).strftime("%Y-%m-%d %H:%M:%S")
        user_expiration_time = user_expiration_time.replace(" ", "T")+"Z"
        self.ret_struct = self.handler.Allocate(None, None, None, {"geni_end_time": user_expiration_time})
        self.assertNotEquals(user_expiration_time, self.ret_struct.get("value").get("geni_slivers")[0].get("geni_expires"))
        
    def test_should_return_rspec(self):
        self.assertNotEquals("", self.ret_struct.get("value").get("geni_rspec"))
    
    def test_should_return_slivers(self):
        self.assertNotEquals([], self.ret_struct.get("value").get("geni_slivers"))
    
    def test_should_fail_when_invalid_credentials(self):
        self.handler.set_credential_manager(MockCredentialManager(False))
        # Allocate must be invoked here because credential manager is different as in setUp
        self.ret_struct = self.handler.Allocate(None, None, None, {})
        self.assertEquals(GENIExceptionManager.FORBIDDEN, self.ret_struct.get("code").get("geni_code"))
    
    def test_should_catch_already_exist_error(self):
        self.handler.set_delegate(MockDelegate(True,True))
        self.ret_struct = self.handler.Allocate(None, None, None, {})
        self.assertEquals(GENIExceptionManager.ALREADYEXISTS, self.ret_struct.get("code").get("geni_code"))
    
    def test_should_catch_allocation_error(self):
        self.handler.set_delegate(MockDelegate(False,False))
        self.ret_struct = self.handler.Allocate(None, None, None, {})
        self.assertEquals(GENIExceptionManager.ERROR, self.ret_struct.get("code").get("geni_code"))
    
if __name__ == "__main__":
    # Allows to run in stand-alone mode
    testcase.main()
