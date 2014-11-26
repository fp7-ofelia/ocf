import os
import sys
import unittest

#PYTHON_DIR ="/opt/ofelia/optin_manager/src/python/"
PYTHON_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../../../../..")
# This is needed because wsgi disallows using stdout
sys.stdout = sys.stderr
os.environ["DJANGO_SETTINGS_MODULE"] = "openflow.optin_manager.settings"
sys.path.insert(0,PYTHON_DIR)
sys.path.append("/opt/ofelia/core/lib/")
sys.path.append("/opt/ofelia/core/lib/am/")
#sys.path.append("/opt/ofelia/expedient/src/python/")

from openflow.optin_manager.geni.v3.drivers.optin import OptinDriver
from am.rspecs.src.geni.v3.openflow.container.link import Link
from am.rspecs.src.geni.v3.openflow.container.dpid import DPID	


class DeviceTest(unittest.TestCase):

    def setUp(self):
        self.driver = OptinDriver()
        self.devices = self.driver.get_all_devices()

    def test_should_get_dpids(self):
        dpids = self.filter_device(DPID)
        self.assertEquals(5, len(dpids))

    def test_should_get_links(self):
        links = self.filter_device(Link)
        print "LINKS:---",len(links)
        from pprint import pprint
        for link in links:
            print "Link: SRC:", link.get_src_dpid().get_datapath(),"port:", link.get_src_port().get_num(), "DST:", link.get_dst_dpid().get_datapath(),"port:", link.get_dst_port().get_num() 

    def filter_device(self, instance):
        devices = list()
        for device in self.devices:
            if isinstance(device, instance):
                devices.append(device)
        return devices

if __name__ == "__main__":
    unittest.main()
