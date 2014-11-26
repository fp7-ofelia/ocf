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
from vt_manager.communication.geni.v3.tests.mockers.resource import ResourceMocker
from am.rspecs.src.geni.v3.container.resource import Resource
from vt_manager.models.reservation import Reservation
from datetime import datetime
from datetime import timedelta

class TestReserveVM(unittest.TestCase):
    
    def setUp(self):
        self.driver = VTAMDriver()
        self.resource = self.get_default_resource_to_reserve()
        self.slice_urn = "urn:publicid:IDN+ocf:i2cat:vtam+slice+mytestslice"
        self.expiration = datetime.utcnow() + timedelta(hours=1)
        self.reserved_resources = self.driver.reserve_vms(self.slice_urn, self.resource)
        self.reservation = Reservation.objects.get(projectName = "ocf.i2cat.vtam.mytestslice")

    def tearDown(self):
        self.reservation.delete()

    def get_default_resource_to_reserve(self):
        resource = ResourceMocker()
        resource.set_component_id( "urn:publicid:IDN+ocf:i2cat:vtam+node+Verdaguer")
        return resource
   
    def test_should_reserve_resource(self):
        self.assertFalse(self.reservation == None)

    def test_should_reserve_resource_with_project_name(self):
        self.assertEquals("ocf.i2cat.vtam.mytestslice", self.reservation.projectName)

    def test_should_reserve_resource_with_slice_name(self):
        self.assertEquals("ocf.i2cat.vtam.mytestslice", self.reservation.sliceName)

    def test_should_reserve_fake_vm_in_Verdaguer(self):
        server_name = self.reservation.server.name
        self.assertEquals("Verdaguer", server_name)

    def test_reserve_should_expire_in_an_hour(self):
        expiration = self.reservation.get_valid_until()
        expiration_formatted = datetime.strptime(expiration, '%Y-%m-%d %H:%M:%S.%f')
        self.assertEquals(self.expiration.hour, expiration_formatted.hour)

    def test_should_return_object(self):
        self.assertFalse(self.reserved_resources == None)
   
    def test_should_return_reservation_object(self):
        self.assertTrue(isinstance(self.reserved_resources, ResourceMocker))

if __name__ == "__main__":
    unittest.main()  

