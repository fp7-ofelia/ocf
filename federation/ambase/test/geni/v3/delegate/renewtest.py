import unittest
from ambase.src.geni.v3.delegate.delegate import GeniV3Delegate
from ambase.test.rm.mockresourcemanager import MockResourceManager
from rspecs.src.geni.v3.container.resource import Resource
from rspecs.src.geni.v3.container.sliver import Sliver

class RenewTest(unittest.TestCase):
    
    def setUp(self):
        self.expiration = "EXPIRATION"
        self.delegate = GeniV3Delegate()
        self.delegate.set_resource_manager(MockResourceManager())
        self.resources = self.delegate.get_resource_manager().get_resources()
        self.renewed = self.delegate.renew([self.resources[0].get_component_id()], self.expiration, True)
        
    def test_should_return_list(self):
        self.assertEquals(list, type(self.renewed))
        
    def test_should_return_resource_in_the_list(self):
        self.assertTrue(isinstance(self.renewed[0], Resource))

    def test_should_renew_resource_expiration(self):
        self.assertEquals(self.expiration, self.renewed[0].get_sliver().get_expiration())        
        
        

        
    


