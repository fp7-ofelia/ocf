import sys
sys.path.append("/opt/ofelia/AMsoil/src/src/vendor/configdb/")
sys.path.append("/opt/ofelia/AMsoil/src/src/")
sys.path.append("/opt/ofelia/AMsoil/src/src/vendor/virtrm")
import amconfigdb
import amconfigdbexceptions
import amsoil.core.pluginmanager as pm
pm.registerService("config", amconfigdb.ConfigDB())
pm.registerService("configexceptions", amconfigdbexceptions)
from models.resources.vtserver import VTServer
import unittest

class VTServerGettersTest(unittest.TestCase):

    def given_this_vtserver(self):
        vtserver = VTServer()
        return vtserver

    def test_should_get_name(self):
        vtserver = self.given_this_vtserver()
        param = "get_name"
        vtserver.name = param
        self.assertEquals(param, vtserver.get_name())
    
    def test_should_get_uuid(self):
        vtserver = self.given_this_vtserver()
        param = "get_uuid"
        vtserver.uuid = param
        self.assertEquals(param, vtserver.get_uuid())

    def test_should_get_memory(self):
        vtserver = self.given_this_vtserver()
        param = 0
        vtserver.memory = param
        self.assertEquals(param, vtserver.get_memory())

    def test_should_get_url(self):
        vtserver = self.given_this_vtserver()
        param = "get_url"
        vtserver.url = param
        self.assertEquals(param, vtserver.get_url())

    def test_should_get_virtualization_technology(self):
        vtserver = self.given_this_vtserver()
        param = "xen"
        vtserver.virtualization_technology = param
        self.assertEquals(param, vtserver.get_virtualization_technology())

    def test_should_get_operating_system_type(self):
        vtserver = self.given_this_vtserver()
        param = "GNU/Linux"
        vtserver.operating_system_type = param
        self.assertEquals(param, vtserver.get_operating_system_type())

    def test_should_get_operating_system_version(self):
        vtserver = self.given_this_vtserver()
        param = "6.0"
        vtserver.operating_system_version = param
        self.assertEquals(param, vtserver.get_operating_system_version())

    def test_should_get_operating_system_distribution(self):
        vtserver = self.given_this_vtserver()
        param = "Debian"
        vtserver.operating_system_distribution = param
        self.assertEquals(param, vtserver.get_operating_system_distribution())

    def test_should_get_available(self):
        vtserver = self.given_this_vtserver()
        param = "get_available"
        vtserver.available = param
        self.assertEquals(param, vtserver.get_available())

    def test_should_get_enabled(self):
        vtserver = self.given_this_vtserver()
        param = "get_enabled"
        vtserver.enabled = param
        self.assertEquals(param, vtserver.get_enabled())

    def test_should_get_number_of_cpus(self):
        vtserver = self.given_this_vtserver()
        param = "get_number_of_cpus"
        vtserver.number_of_cpus = param
        self.assertEquals(param, vtserver.get_number_of_cpus())

    def test_should_get_cpu_frequency(self):
        vtserver = self.given_this_vtserver()
        param = "get_cpu_frequency"
        vtserver.cpu_frequency = param
        self.assertEquals(param, vtserver.get_cpu_frequency())

    def test_should_get_disc_space_gb(self):
        vtserver = self.given_this_vtserver()
        param = "get_disc_space_gb"
        vtserver.disc_space_gb = param
        self.assertEquals(param, vtserver.get_disc_space_gb())

if __name__ == '__main__':
    unittest.main()
