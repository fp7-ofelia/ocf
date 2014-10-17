import unittest
from ambase.src.geni.v3.delegate.delegate import GeniV3Delegate
from ambase.test.rm.mockresourcemanager import MockResourceManager
from rspecs.src.geni.v3.container.resource import Resource

class PerformOperationalActionTest(unittest.TestCase):
    
    def setUp(self):
        self.urns = list()
        self.delegate = GeniV3Delegate()
        self.delegate.set_resource_manager(MockResourceManager())
        self.resources = self.delegate.get_resource_manager().get_resources()
        self.started = self.delegate.perform_operational_action([self.resources[0].get_component_id()], "geni_start",True)
        self.stopped = self.delegate.perform_operational_action([self.resources[1].get_component_id()], "geni_stop",True)
        self.rebooted = self.delegate.perform_operational_action([self.resources[2].get_component_id()], "geni_restart",True)
        
    def test_perform_op_action_should_return_list_when_start(self):
        self.assertEquals(list, type(self.started))
    
    def test_perform_op_action_should_return_list_when_stop(self):
        self.assertEquals(list, type(self.stopped))
    
    def test_perform_op_action_should_return_list_when_reboot(self):
        self.assertEquals(list, type(self.rebooted))
        
    def test_perform_op_action_should_return_lists_of_resources_when_start(self):
        self.assertTrue(isinstance(self.started[0], Resource))
    
    def test_perform_op_action_should_return_lists_of_resources_when_stop(self):
        self.assertTrue(isinstance(self.stopped[0], Resource))
    
    def test_perform_op_action_should_return_lists_of_resources_when_reboot(self):
        self.assertTrue(isinstance(self.rebooted[0], Resource))
            
    def test_should_start_resource(self):
        self.assertEquals("geni_ready", self.started[0].get_operational_state())
    
    def test_should_stop_resource(self):
        self.assertEquals("geni_notready", self.stopped[0].get_operational_state())
        
    def test_should_reboot_resource(self):
        self.assertEquals("geni_ready", self.rebooted[0].get_operational_state())
    
    def test_should_raise_exception_when_unknown_action(self):
        self.assertRaises(Exception,self.delegate.perform_operational_action,[self.resources[3].get_component_id(), "unknown_action",True])

if __name__ == "__main__":
    unittest.main()