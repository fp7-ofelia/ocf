import unittest
from ambase.src.geni.v3.delegate.delegate import GeniV3Delegate
from ambase.test.rm.mockresourcemanager import MockResourceManager
from rspecs.src.geni.v3.container.sliver import Sliver
from rspecs.src.geni.v3.container.resource import Resource

class AllocateTest(unittest.TestCase):
    
    def setUp(self):
        self.urns = list()
        self.delegate = GeniV3Delegate()
        self.delegate.set_resource_manager(MockResourceManager())
        self.reserved_resources = self.get_reservation()
        self.allocated = self.delegate.reserve("urn:publicID:test:allocation+myauthority+cm" ,self.reserved_resources, None)

    def test_should_return_success_result(self):
        self.assertTrue(self.allocated)

    def test_should_have_all_resources_reserved(self):
        allocated = self.filter_by_allocated()       
        self.assertEquals(len(self.reserved_resources), len(allocated))

    def get_reservation(self):
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
            r.set_allocation_state("Free")
            s.set_resource(r)
            r.set_sliver(s)
            resources.append(r)
        return resources
    
    def filter_by_allocated(self):
        resources  = self.delegate.get_resource_manager().get_resources(self.urns)
        return resources 
        