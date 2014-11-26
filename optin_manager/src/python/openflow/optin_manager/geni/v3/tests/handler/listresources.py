import os
import sys
from os.path import dirname, join

PYTHON_DIR ="/opt/ofelia/optin_manager/src/python/"
# This is needed because wsgi disallows using stdout
sys.stdout = sys.stderr
os.environ['DJANGO_SETTINGS_MODULE'] = 'openflow.optin_manager.settings'
sys.path.insert(0,PYTHON_DIR)
sys.path.append("/opt/ofelia/core/lib/")
sys.path.append("/opt/ofelia/core/lib/am/")

from openflow.optin_manager.geni.v3.drivers.optin import OptinDriver
from am.rspecs.src.geni.v3.openflow.container.link import Link
from am.rspecs.src.geni.v3.openflow.container.dpid import DPID	
from am.rspecs.src.geni.v3.openflow.manager import OpenFlowRSpecManager

import unittest

class ListResourcesTest(unittest.TestCase):

    def setUp(self):
        self.driver = OptinDriver()
        self.devices = self.driver.get_all_devices()
        self.manager = OpenFlowRSpecManager()

    def test_should_list_resources(self):
        print self.manager.compose_advertisement(self.devices)

if __name__ == "__main__":
    unittest.main()

