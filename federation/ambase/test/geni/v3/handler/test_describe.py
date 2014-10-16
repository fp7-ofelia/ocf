from ambase.src.geni.exceptions.manager import GENIExceptionManager
from ambase.src.geni.v3.handler.handler import GeniV3Handler
from ambase.test.utils import testcase
from ambase.test.utils.mockcredentialmanager import MockCredentialManager
from ambase.test.utils.mockdelegate import MockDelegate
from ambase.test.utils.mockrspecmanager import MockRSpecManager
import base64
from lxml import etree


class TestDescribe(testcase.TestCase):
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
        self.ret_struct = self.handler.Describe(None,None, options=self.options)

        
    def tearDown(self):
        self.handler = None
        
    def test_should_describe(self):
        self.assertEquals(GENIExceptionManager.SUCCESS, self.ret_struct.get('code').get('geni_code'))
    
    def test_fail_when_invalid_options(self):
        value = self.handler.Describe(None,None, options={})
        self.assertEquals(GENIExceptionManager.BADARGS, value.get('code').get('geni_code'))
    
    def test_should_fail_when_invalid_credentials(self):
        self.handler.set_credential_manager(MockCredentialManager(False))
        value = self.handler.Describe(None,None, options=self.options)
        self.assertEquals(GENIExceptionManager.FORBIDDEN, value.get('code').get('geni_code'))
    
    def test_should_send_compressed_output_when_geni_compressed(self):
        options = {"geni_rspec_version": {"type": "geni", "version": "3"}, 'geni_compressed':True}
        value = self.handler.Describe(None,None, options=options)
        #If it can decode, it raise an Exception
        try:
            geni_rspec_uncompressed = etree.fromstring(value.get("value").get("geni_rspec"))
            geni_rspec_compressed = geni_rspec_uncompressed
        except:
            geni_rspec_compressed = base64.b64decode(value.get("value").get("geni_rspec"))
            #geni_rspec_compressed = base64.decodestring(self.ret_struct.get("value").get("geni_rspec"))
        self.assertEquals(str, type(geni_rspec_compressed))
        
    def test_should_return_correct_value_structure(self):
        struct = self.get_expected_return_structure().keys()
        struct.sort()
        obtained = self.ret_struct.get("value").keys()
        obtained.sort()
        self.assertEquals(struct, obtained)
        
    def test_should_return_correct_sliver_value_structure(self):
        struct = self.get_geni_slivers_content().keys()
        struct.sort()
        obtained = self.ret_struct.get("value").get("geni_slivers")[0].keys()
        obtained.sort()
        self.assertEquals(struct, obtained)
        
    def get_expected_return_structure(self):
        struct = {"geni_rspec" : "None",
                  "geni_slivers" : [],
                  "geni_urn": "None",}
        return struct
    
    def get_geni_slivers_content(self):
        return { "geni_sliver_urn": "urn",
                 "geni_allocation_status": "string",
                 "geni_operational_status": "string",
                 "geni_expires":"String"}
    
if __name__ == '__main__':
    # Allows to run in stand-alone mode
    testcase.main()
