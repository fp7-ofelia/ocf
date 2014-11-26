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

from vt_manager.communication.geni.v3.configurators.handlerconfigurator import HandlerConfigurator
from vt_manager.communication.geni.v3.drivers.vtam import VTAMDriver
from vt_manager.communication.geni.v3.managers.vtam import VTAMRM

import unittest

class TestRMConfigurator(unittest.TestCase):
    
    def setUp(self):
        self.configurator = HandlerConfigurator
        self.configured_rm = self.configurator.get_vt_am_resource_manager()

    def test_should_get_vt_am_resource_amanger_instance(self):
        self.assertTrue(isinstance(self.configured_rm, VTAMRM))
  
    def test_should_get_not_null_driver(self):
        self.assertFalse(self.configured_rm.get_driver() == None)


if __name__ == "__main__":
    unittest.main()
    
      
