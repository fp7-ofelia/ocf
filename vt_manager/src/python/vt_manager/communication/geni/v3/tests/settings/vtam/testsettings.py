import sys
sys.path.append("/opt/ofelia/core/lib/am/")
sys.path.append("/opt/ofelia/core/lib/")
sys.path.append("/opt/ofelia/vt_manager/src/python/")

import os
import sys
from os.path import dirname, join
sys.stdout = sys.stderr
os.environ['DJANGO_SETTINGS_MODULE'] = 'vt_manager.settings.settingsLoader'
import unittest

from vt_manager.communication.geni.v3.settings.vtam import VTAMConfig
from am.settings.src.settings import Settings

class TestSettings(unittest.TestCase):

    def setUp(self):
       self.setting_manager = VTAMConfig

    def test_should_have_hrn_setting(self):
       self.assertNotEquals(Settings.HRN, self.setting_manager.HRN)

    def test_shold_have_trusted_roots_directory(self):
       self.assertNotEquals(Settings.TRUSTED_ROOTS_DIR, self.setting_manager.TRUSTED_ROOTS_DIR)

if __name__ == "__main__":
    unittest.main()
