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
from vt_manager.communication.geni.v3.managers.vtam import VTAMRM

from am.ambase.src.geni.v3.handler.handler import GeniV3Handler as Handler

import unittest

class TestHandlerConfigurator(unittest.TestCase):
    
    def setUp(self):
        self.configurator = HandlerConfigurator
        self.configured_handler = self.configurator.configure_handler()

    def test_should_get_vt_am_handler_instance(self):
        self.assertTrue(isinstance(self.configured_handler, Handler))

    def test_should_get_rspec_manager_not_null(self):
        self.assertFalse(self.configured_handler.get_rspec_manager() == None)
   
    def test_should_get_credential_manager_not_null(self):
        self.assertFalse(self.configured_handler.get_credential_manager() == None)

    def test_should_get_delegate_not_null(self):
        self.assertFalse(self.configured_handler.get_delegate() == None)

    def test_should_get_geni_exception_manager_not_null(self):
        self.assertFalse(self.configured_handler.get_geni_exception_manager() == None)

if __name__ == "__main__":
    unittest.main()
