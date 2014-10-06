import unittest
from ambase.src.geni.v3.delegate.delegate import GeniV3Delegate

class TestGetVersion(unittest.TestCase):
    """ Testing very basic behaviour to see 
        whether the Handler is able to respond
        with error_results or success_results  
    """
    def setUp(self):
        self.delegate = GeniV3Delegate()
        self.version = self.delegate.get_version()

    def test_should_return_success_result(self):
        self.assertEquals(dict, type(self.version))

    def test_should_contain_main_keys(self):
        expected = ['geni_ad_rspec_versions', 'geni_request_rspec_versions', 'geni_am_type', 'geni_api', 'geni_api_versions', 'geni_am_code', 'geni_credential_types']
        expected.sort()
        keys = self.version.keys()
        keys.sort()
        self.assertEquals(expected, keys)
        
    def test_geni_api_should_be_int(self):
        geni_api = self.version['geni_api']
        self.assertEquals(int, type(geni_api))
        
    def test_api_versions_should_be_struct(self):
        geni_api_versions = self.version['geni_api_versions']
        self.assertEquals(dict, type(geni_api_versions))
        
    def test_geni_request_rspec_versions_should_be_list(self):
        geni_req_rspec_versions = self.version['geni_request_rspec_versions']
        self.assertEquals(list, type(geni_req_rspec_versions))
        
    def test_geni_ad_rspec_versions_should_be_list(self):
        geni_ad_rspec_versions = self.version['geni_ad_rspec_versions']
        self.assertEquals(list,type(geni_ad_rspec_versions))
        
    def test_geni_credential_types_should_be_list(self):
        geni_cred_types = self.version['geni_credential_types']
        self.assertEquals(list, type(geni_cred_types))
        
        

