from ambase.src.geni.exceptions.manager import GENIExceptionManager
from ambase.src.geni.v3.handler.handler import GeniV3Handler
from ambase.test.utils import testcase
from ambase.test.utils.mockcredentialmanager import MockCredentialManager
from ambase.test.utils.mockdelegate import MockDelegate
from ambase.test.utils.mockrspecmanager import MockRSpecManager
import base64


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
        self.options = {"geni_rspec_version":{"type":1, "version":"2"}}
        
    def tearDown(self):
        self.handler = None
        
    def test_should_describe(self):
        value = self.handler.Describe(None,None, options=self.options)
        self.assertEquals(GENIExceptionManager.SUCCESS, value.get('code').get('geni_code'))
    
    def test_fail_when_invalid_options(self):
        value = self.handler.Describe(None,None, options={})
        self.assertEquals(GENIExceptionManager.BADARGS, value.get('code').get('geni_code'))
    
    def test_should_fail_when_invalid_credentials(self):
        self.handler.set_credential_manager(MockCredentialManager(False))
        value = self.handler.Describe(None,None, options=self.options)
        self.assertEquals(GENIExceptionManager.FORBIDDEN, value.get('code').get('geni_code'))
    
    def test_should_send_compressed_output_when_geni_compressed(self):
        self.options['geni_compressed'] = True
        value = self.handler.ListResources(None, self.options)
        #If it can decode, it raise an Exception
        self.assertEquals(str,type(base64.decodestring(value.get('value'))))
    
if __name__ == '__main__':
    # Allows to run in stand-alone mode
    testcase.main()
