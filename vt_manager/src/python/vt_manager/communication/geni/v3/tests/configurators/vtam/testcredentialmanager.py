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
from am.credentials.src.manager.manager import CredentialManager

import unittest

class TestCredentialManagerConfigurator(unittest.TestCase):
    
    def setUp(self):
        self.configurator = HandlerConfigurator
        self.configured_credential_manager = self.configurator.get_vt_am_credential_manager()

    def test_should_get_rspec_manager_instance(self):
        self.assertTrue(isinstance(self.configured_credential_manager, CredentialManager))

if __name__ == "__main__":
    unittest.main()
    
      
