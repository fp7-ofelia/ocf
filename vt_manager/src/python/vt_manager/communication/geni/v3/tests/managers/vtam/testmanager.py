import sys
import os
sys.path.append("/opt/ofelia/core/lib/am/")
sys.path.append("/opt/ofelia/core/lib/")
sys.path.append("/opt/ofelia/vt_manager/src/python/")

from os.path import dirname, join
# This is needed because wsgi disallows using stdout
sys.stdout = sys.stderr
os.environ['DJANGO_SETTINGS_MODULE'] = 'vt_manager.settings.settingsLoader'

from vt_manager.communication.geni.v3.managers.vtam import VTAMRM
from  vt_manager.communication.geni.v3.tests.mockers.driver import VTAMDriverMocker
from vt_manager.communication.geni.v3.tests.mockers.resource import ResourceMocker
import unittest

class TestManager(unittest.TestCase):

    def setUp(self):
        self.manager = VTAMRM()
        self.manager.set_driver(VTAMDriverMocker())
        self.urns = ["urn1","urn2"]

    def test_should_get_only_servers(self):
        resources = self.manager.get_resources(urns=None)
        self.assertEquals(5, len(resources))

    def test_should_get_servers_with_slivers(self):
        resources = self.manager.get_resources(self.urns)
        self.assertEquals(20, len(resources))

    def test_should_start_resources(self):
        result = self.manager.start_resources(self.urns, True)[0]
        self.assertTrue(isinstance(result, ResourceMocker))

    def test_should_stop_resources(self):
        result = self.manager.stop_resources(self.urns, True)[0]
        self.assertTrue(isinstance(result, ResourceMocker))

    def test_should_reboot_resources(self):
        result = self.manager.reboot_resources(self.urns, True)[0]
        self.assertTrue(isinstance(result, ResourceMocker))

    def test_should_delete_resources(self):
        result = self.manager.delete_resources(self.urns, True)[0]
        self.assertTrue(isinstance(result, ResourceMocker))

    def test_sould_renew_resources(self):
        result = self.manager.renew_resources("expiration",self.urns, True)[0]
        self.assertTrue(isinstance(result, ResourceMocker))
    
if __name__ == "__main__":
    unittest.main()

