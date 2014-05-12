import sys
sys.path.append("/opt/ofelia/AMsoil/src/src/vendor/configdb/")
sys.path.append("/opt/ofelia/AMsoil/src/src/")
sys.path.append("/opt/ofelia/AMsoil/src/src/vendor/virtrm")
import amconfigdb
import amconfigdbexceptions
import amsoil.core.pluginmanager as pm
pm.registerService("config", amconfigdb.ConfigDB())
pm.registerService("configexceptions", amconfigdbexceptions)
from models.resources.vmallocated import VMAllocated
import unittest


class VMAllocatedSettersTest(unittest.TestCase):

    def given_this_vm(self):
        vm_allocated = VMAllocated()
        return vm_allocated

    def test_should_set_disc_space_gb(self):
        vm_allocated = self.given_this_vm()
        param = "set_disc_space_gb"
        vm_allocated.set_disc_space_gb(param)
        self.assertEquals(param, vm_allocated.disc_space_gb)

    def test_should_set_do_save(self):
        vm_allocated = self.given_this_vm()
        param = "set_do_save"
        vm_allocated.set_do_save(param)
        self.assertEquals(param, vm_allocated.do_save)

    def test_should_set_memory(self):
        vm_allocated = self.given_this_vm()
        param = "set_memory"
        vm_allocated.set_memory(param)
        self.assertEquals(param, vm_allocated.memory)

    def test_should_set_name(self):
        vm_allocated = self.given_this_vm()
        param = "set_name"
        vm_allocated.set_name(param)
        self.assertEquals(param, vm_allocated.name)

    def test_should_set_number_of_cpus(self):
        vm_allocated = self.given_this_vm()
        param = "set_number_of_cpus"
        vm_allocated.set_number_of_cpus(param)
        self.assertEquals(param, vm_allocated.number_of_cpus)

    def test_should_set_project_id(self):
        vm_allocated = self.given_this_vm()
        param = "set_project_id"
        vm_allocated.set_project_id(param)
        self.assertEquals(param, vm_allocated.project_id)

    def test_should_set_project_name(self):
        vm_allocated = self.given_this_vm()
        param = "set_project_name"
        vm_allocated.set_project_name(param)
        self.assertEquals(param, vm_allocated.project_name)

    def test_should_set_slice_id(self):
        vm_allocated = self.given_this_vm()
        param = "set_slice_id"
        vm_allocated.set_slice_id(param)
        self.assertEquals(param, vm_allocated.slice_id)

    def test_should_set_slice_name(self):
        vm_allocated = self.given_this_vm()
        param = "set_slice_name"
        vm_allocated.set_slice_name(param)
        self.assertEquals(param, vm_allocated.slice_name)

    def test_should_set_virtualization_technology(self):
        vm_allocated = self.given_this_vm()
        param = "xen"
        vm_allocated.set_virtualization_technology(param)
        self.assertEquals(param, vm_allocated.virtualization_technology)

if __name__ == '__main__':
    unittest.main()

