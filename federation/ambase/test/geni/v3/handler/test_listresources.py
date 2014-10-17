from ambase.src.geni.exceptions.manager import GENIExceptionManager
from ambase.src.geni.v3.handler.handler import GeniV3Handler
from ambase.src.geni.v3.delegate.delegate import GeniV3Delegate
from ambase.test.utils import testcase
from ambase.test.utils.mockcredentialmanager import MockCredentialManager
from ambase.test.utils.mockdelegate import MockDelegate
from ambase.test.utils.mockrspecmanager import MockRSpecManager
from lxml import etree

class TestListResources(testcase.TestCase):
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
        self.options = {"geni_rspec_version": {"type": "geni", "version": "3"}}
        self.ret_struct = self.handler.ListResources(None, self.options)
        
    def tearDown(self):
        self.handler = None
        
    def test_should_list_resources(self):
        self.assertEquals(GENIExceptionManager.SUCCESS, self.ret_struct.get("code").get("geni_code"))
        
    def test_should_fail_when_list_resources_without_proper_options(self):
        self.ret_struct = self.handler.ListResources(None, options = {})
        self.assertEquals(GENIExceptionManager.BADARGS, self.ret_struct.get("code").get("geni_code"))
    
    def test_should_fail_when_list_resources_without_proper_geni_rspec_version(self):
        self.options = {"geni_rspec_version": {"type": 1, "version": "2"}}
        self.ret_struct = self.handler.ListResources(None, self.options)
        self.assertEquals(GENIExceptionManager.BADVERSION, self.ret_struct.get("code").get("geni_code"))
    
    def test_should_return_compressed_output_when_geni_compressed(self):
        self.options["geni_compressed"] = True
        self.ret_struct = self.handler.ListResources(None, self.options)
        # An XML can be decoded by base64.b64decode, thus we should try first with something particular
        try:
            geni_rspec_uncompressed = etree.fromstring(self.ret_struct.get("value"))
            geni_rspec_compressed = geni_rspec_uncompressed
        except:
            import base64
            geni_rspec_compressed = base64.b64decode(self.ret_struct.get("value"))
            #geni_rspec_compressed = base64.decodestring(self.ret_struct.get("value"))
        self.assertEquals(str, type(geni_rspec_compressed))
    
    def test_should_return_uncompressed_output_when_not_geni_compressed(self):
        from lxml import etree
        try:
            geni_rspec_uncompressed = etree.fromstring(self.ret_struct.get("value"))
        except:
            geni_rspec_uncompressed = None
        self.assertEquals(etree._Element, type(geni_rspec_uncompressed))

    def test_shoud_return_error_when_invalid_credentials(self):
        self.handler.set_credential_manager(MockCredentialManager(False))
        # ListResources must be invoked here because credential manager is different as in setUp
        self.ret_struct = self.handler.ListResources(None, self.options)
        self.assertEquals(GENIExceptionManager.FORBIDDEN, self.ret_struct.get("code").get("geni_code"))
    
    def test_should_return_correct_sliver_value_structure(self):
        self.assertEquals(str, type(self.ret_struct.get("value")))
    
if __name__ == "__main__":
    # Allows to run in stand-alone mode
    testcase.main()
