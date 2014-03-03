import sys
sys.path.append("/opt/ofelia/AMsoil/src/vendor/configdb/")
sys.path.append("/opt/ofelia/AMsoil/src/")
sys.path.append("/opt/ofelia/AMsoil/src/vendor/virtrm")
import amconfigdb
import amconfigdbexceptions
import amsoil.core.pluginmanager as pm
pm.registerService("config", amconfigdb.ConfigDB())
pm.registerService("configexceptions", amconfigdbexceptions)
from models.resources.vmallocated import VMAllocated
import unittest


class VMAllocatedGettersTest(unittest.TestCase):

    def given_this_vm(self):
        vm_allocated = VMAllocated()
        return vm_allocated

    def test_should_get_disc_space_gb(self):
        vm_allocated = self.given_this_vm()
        param = 0
        vm_allocated.disc_space_gb = param
        self.assertEquals(param, vm_allocated.get_disc_space_gb())

    def test_should_get_memory(self):
        vm_allocated = self.given_this_vm()
        param = 0
        vm_allocated.memory = param
        self.assertEquals(param, vm_allocated.get_memory())

    def test_should_get_name(self):
        vm_allocated = self.given_this_vm()
        param = "vm"
        vm_allocated.name = param
        self.assertEquals(param, vm_allocated.get_name())

    def test_should_get_uuid(self):
        vm_allocated = self.given_this_vm()
        param = "vm"
        vm_allocated.uuid = param
        self.assertEquals(param, vm_allocated.get_uuid())

    def test_should_get_number_of_cpus(self):
        vm_allocated = self.given_this_vm()
        param = 0
        vm_allocated.number_of_cpus = param
        self.assertEquals(param, vm_allocated.get_number_of_cpus())

    def test_should_get_project_id(self):
        vm_allocated = self.given_this_vm()
        param = "vm"
        vm_allocated.project_id = param
        self.assertEquals(param, vm_allocated.get_project_id())

    def test_should_get_project_name(self):
        vm_allocated = self.given_this_vm()
        param = "vm"
        vm_allocated.project_name = param
        self.assertEquals(param, vm_allocated.get_project_name())

    def test_should_get_slice_id(self):
        vm_allocated = self.given_this_vm()
        param = "vm"
        vm_allocated.slice_id = param
        self.assertEquals(param, vm_allocated.get_slice_id())

    def test_should_get_slice_name(self):
        vm_allocated = self.given_this_vm()
        param = "vm"
        vm_allocated.slice_name = param
        self.assertEquals(param, vm_allocated.get_slice_name())

    def test_should_get_virtualization_technology(self):
        vm_allocated = self.given_this_vm()
        param = "xen"
        vm_allocated.virtualization_technology = param
        self.assertEquals(param, vm_allocated.get_virtualization_technology())
    
    def test_should_get_do_save(self):
        vm_allocated = self.given_this_vm()
        param = "vm"
        vm_allocated.do_save = param
        self.assertEquals(param, vm_allocated.get_do_save())

if __name__ == '__main__':
    unittest.main()

