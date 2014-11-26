import sys
sys.path.append("/opt/ofelia/core/lib/am/")
sys.path.append("/opt/ofelia/core/lib/")
sys.path.append("/opt/ofelia/vt_manager/src/python/")

import os
import sys
from os.path import dirname, join
import copy

# This is needed because wsgi disallows using stdout
sys.stdout = sys.stderr

os.environ['DJANGO_SETTINGS_MODULE'] = 'vt_manager.settings.settingsLoader'

#sys.path.insert(0,PYTHON_DIR)


import unittest
from vt_manager.communication.geni.v3.drivers.vtam import VTAMDriver
from vt_manager.communication.geni.v3.tests.mockers.reservation import ReservationMocker
from vt_manager.communication.geni.v3.tests.mockers.server import ServerMocker

from vt_manager.communication.utils.XmlHelper import XmlHelper, XmlCrafter
from vt_manager.communication.geni.v3.tests.drivers.vtam.expected_outputs import DEFAULT_VM_PARAMS

class TestTranslatorToDict(unittest.TestCase):
    
    def setUp(self):
        self.driver = VTAMDriver()
        self.vm_params = self.get_default_vm_params()
        self.vm_class = self.prepare_vm_class()       
        self.driver.vm_dict_to_class(self.vm_params, self.vm_class)

    def get_default_vm_params(self):
        return DEFAULT_VM_PARAMS

    def prepare_vm_class(self):
        rspec = XmlHelper.getSimpleActionQuery()
	actionClassEmpty = copy.deepcopy(rspec.query.provisioning.action[0])
        actionClassEmpty.type_ = "create"
        rspec.query.provisioning.action.pop()
        return actionClassEmpty.server.virtual_machines[0]
   

    def test_should_set_correct_name(self):
        self.assertEquals(self.vm_params.get("name"), self.vm_class.name)   
 
    def test_should_set_correct_uuid(self):
        self.assertEquals(self.vm_params.get("uuid"), self.vm_class.uuid)

    def test_should_set_correct_status(self):
        self.assertEquals(self.vm_params.get("state"), self.vm_class.status)

    def test_should_set_correct_project_id(self):
        self.assertEquals(self.vm_params.get("project-id"), self.vm_class.project_id)    

    def test_should_set_correct_project_name(self):
        self.assertEquals(self.vm_params.get("project-name"), self.vm_class.project_name)  
 
    def test_should_set_correct_slice_name(self):
        self.assertEquals(self.vm_params.get("slice-name"), self.vm_class.slice_name)
 
    def test_should_set_correct_slice_id(self):
        self.assertEquals(self.vm_params.get("slice-id"), self.vm_class.slice_id)

    def test_should_set_correct_operating_system_type(self):
        self.assertEquals(self.vm_params.get("operating-system-type"), self.vm_class.operating_system_type)

    def test_should_set_correct_operating_system_version(self):
        self.assertEquals(self.vm_params.get("operating-system-version"), self.vm_class.operating_system_version)

    def test_should_set_correct_operating_system_distro(self):
        self.assertEquals(self.vm_params.get("operating-system-distribution"), self.vm_class.operating_system_distribution)

    def test_should_set_correct_virtualization_type(self):
        self.assertEquals(self.vm_params.get("virtualization-type"), self.vm_class.virtualization_type)

    def test_should_set_correct_virtualization_setup_type(self):
        self.assertEquals(self.vm_params.get("virtualization-setup-type"), self.vm_class.xen_configuration.virtualization_setup_type)

    def test_should_set_correct_project_name(self):
        self.assertEquals(self.vm_params.get("server-id"), self.vm_class.server_id)

    def test_should_set_correct_memory(self):
        self.assertEquals(self.vm_params.get("memory-mb"), self.vm_class.xen_configuration.memory_mb)

    def test_should_set_correct_hd_setup_type(self):
        self.assertEquals(self.vm_params.get("hd-setup-type"), self.vm_class.xen_configuration.hd_setup_type)

    def test_should_set_correct_project_name(self):
        self.assertEquals(self.vm_params.get("hd-origin-path"), self.vm_class.xen_configuration.hd_origin_path)

if __name__ == "__main__":
    unittest.main()  
    
