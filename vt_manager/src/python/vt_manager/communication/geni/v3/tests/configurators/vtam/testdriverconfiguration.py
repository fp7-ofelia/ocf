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

import unittest

class TestDriverConfigurator(unittest.TestCase):
    
    def setUp(self):
        self.configurator = HandlerConfigurator
        self.configured_driver = self.configurator.get_vt_am_driver()

    def test_should_get_vt_am_driver_instance(self):
        self.assertTrue(isinstance(self.configured_driver, VTAMDriver))

if __name__ == "__main__":
    unittest.main()
    
      
