import unittest
from ambase.src.geni.v3.delegate.delegate import GeniV3Delegate
from ambase.test.rm.mockresourcemanager import MockResourceManager
from rspecs.src.geni.v3.container.resource import Resource
from rspecs.src.geni.v3.container.sliver import Sliver

class ProvisionTest(unittest.TestCase):
    
    def setUp(self):
        self.urns = list()
        self.delegate = GeniV3Delegate()
        self.delegate.set_resource_manager(MockResourceManager(self.add_reservations()))
        self.manifest = self.delegate.create(self.urns)
        
    def test_should_return_success_result(self):
        self.assertEquals(list, type(self.manifest))
        
    def test_should_return_this_resources_list(self):
        resource_manifest = "[Resource [ _Resource__allocation_state=provisioned, _Resource__available=None, _Resource__component_id=urn:publicid:mocked+resource+0, _Resource__component_manager_id=urn:publicid:mocked+resource+0, _Resource__component_manager_name=urn:publicid:mocked+resource+0, _Resource__component_name=urn:publicid:mocked+resource+0, _Resource__exclusive=None, _Resource__id=0, _Resource__operational_state=None, _Resource__sliver=Sliver [ _Sliver__allocation_status=None, _Sliver__client_id=None, _Sliver__expiration=None, _Sliver__name=None, _Sliver__operational_status=None, _Sliver__services={}, _Sliver__slice_urn=None, _Sliver__type=None, _Sliver__urn=urn:publicid:mocked:slice+resource+0, ], _Resource__uuid=0, ], Resource [ _Resource__allocation_state=provisioned, _Resource__available=None, _Resource__component_id=urn:publicid:mocked+resource+1, _Resource__component_manager_id=urn:publicid:mocked+resource+1, _Resource__component_manager_name=urn:publicid:mocked+resource+1, _Resource__component_name=urn:publicid:mocked+resource+1, _Resource__exclusive=None, _Resource__id=1, _Resource__operational_state=None, _Resource__sliver=Sliver [ _Sliver__allocation_status=None, _Sliver__client_id=None, _Sliver__expiration=None, _Sliver__name=None, _Sliver__operational_status=None, _Sliver__services={}, _Sliver__slice_urn=None, _Sliver__type=None, _Sliver__urn=urn:publicid:mocked:slice+resource+1, ], _Resource__uuid=1, ]]"
        self.assertEquals(resource_manifest, str(self.manifest))
    
    def test_should_have_provisioned_resources(self):
        for r in self.manifest:
            self.assertEquals("provisioned", r.get_allocation_state())    
        
    def add_reservations(self):
        resources = list()
        for i in range(0,2):
            r = Resource()
            r.set_id(i)
            r.set_uuid(i)
            #r.set_status("READY")
            r.set_component_id("urn:publicid:mocked+resource+%d" %i)
            r.set_component_manager_id("urn:publicid:mocked+resource+%d" %i)
            r.set_component_name("urn:publicid:mocked+resource+%d" %i)
            r.set_component_manager_name("urn:publicid:mocked+resource+%d" %i)
            s = Sliver()
            s.set_urn("urn:publicid:mocked:slice+resource+%d" %i)
            self.urns.append("urn:publicid:mocked:slice+resource+%d" %i)
            r.set_allocation_state("RESERVED")
            s.set_resource(r)
            r.set_sliver(s)
            resources.append(r)
        return resources
        
if __name__ == "__main__":
    unittest.main()