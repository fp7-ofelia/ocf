import sys
sys.path.append("/opt/ofelia/core/lib/am/")
sys.path.append("/opt/ofelia/core/lib/")
sys.path.append("/opt/ofelia/vt_manager/src/python/")

import os
import sys
from os.path import dirname, join


# This is needed because wsgi disallows using stdout
sys.stdout = sys.stderr

os.environ['DJANGO_SETTINGS_MODULE'] = 'vt_manager.settings.settingsLoader'

#sys.path.insert(0,PYTHON_DIR)


import unittest
from vt_manager.communication.geni.v3.drivers.vtam import VTAMDriver
from vt_manager.communication.geni.v3.tests.mockers.reservation import ReservationMocker
from vt_manager.communication.geni.v3.tests.mockers.server import ServerMocker

class TestTranslatorToDict(unittest.TestCase):
    
    def setUp(self):
        self.driver = VTAMDriver()
        self.reservation = self.get_default_reservation()
        self.vm_params = self.driver.get_default_vm_parameters(self.reservation)

    def get_default_reservation(self):
        r = ReservationMocker()
        r.set_project_id("test-project")
        r.set_slice_id("test-slice")
        r.set_slice_name("test-slice-name")
        r.set_project_name("test-project-name")
        r.set_uuid("THIS-IS-THE-UUID-OF-A-VM")  
        s = ServerMocker()
        s.set_uuid("THIS-IS-THE-UUID-OF-A-SERVER")
        s.set_virt_tech("paravirtualization")
        r.server = s
        return r
   
    def test_shoud_return_correct_default_vm_params(self):
        self.assertFalse(None in self.vm_params.values())  
   

if __name__ == "__main__":
    unittest.main()  
    
