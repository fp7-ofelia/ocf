import unittest
from ambase.src.geni.v3.delegate.delegate import GeniV3Delegate
from ambase.test.rm.mockresourcemanager import MockResourceManager

class ListResourcesTest(unittest.TestCase):
    
    def setUp(self):
        self.delegate = GeniV3Delegate()
        self.delegate.set_resource_manager(MockResourceManager())
        self.resources = self.delegate.list_resources()

    def test_should_return_success_result(self):
        self.assertEquals(list, type(self.resources))
        
    def test_should_return_this_resources_list(self):
        resource_list_string = "[Resource [ _Resource__allocation_state=Free, _Resource__available=None, _Resource__component_id=urn:publicid:mocked+resource+0, _Resource__component_manager_id=urn:publicid:mocked+resource+0, _Resource__component_manager_name=urn:publicid:mocked+resource+0, _Resource__component_name=urn:publicid:mocked+resource+0, _Resource__exclusive=None, _Resource__id=0, _Resource__operational_state=None, _Resource__sliver=None, _Resource__uuid=0, ], Resource [ _Resource__allocation_state=Free, _Resource__available=None, _Resource__component_id=urn:publicid:mocked+resource+1, _Resource__component_manager_id=urn:publicid:mocked+resource+1, _Resource__component_manager_name=urn:publicid:mocked+resource+1, _Resource__component_name=urn:publicid:mocked+resource+1, _Resource__exclusive=None, _Resource__id=1, _Resource__operational_state=None, _Resource__sliver=None, _Resource__uuid=1, ], Resource [ _Resource__allocation_state=Free, _Resource__available=None, _Resource__component_id=urn:publicid:mocked+resource+2, _Resource__component_manager_id=urn:publicid:mocked+resource+2, _Resource__component_manager_name=urn:publicid:mocked+resource+2, _Resource__component_name=urn:publicid:mocked+resource+2, _Resource__exclusive=None, _Resource__id=2, _Resource__operational_state=None, _Resource__sliver=None, _Resource__uuid=2, ], Resource [ _Resource__allocation_state=Free, _Resource__available=None, _Resource__component_id=urn:publicid:mocked+resource+3, _Resource__component_manager_id=urn:publicid:mocked+resource+3, _Resource__component_manager_name=urn:publicid:mocked+resource+3, _Resource__component_name=urn:publicid:mocked+resource+3, _Resource__exclusive=None, _Resource__id=3, _Resource__operational_state=None, _Resource__sliver=None, _Resource__uuid=3, ]]"
        self.assertEquals(resource_list_string, str(self.resources))
        
if __name__ == "__main__":
    unittest.main()
        