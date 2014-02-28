import sys
sys.path.append("/opt/ofelia/AMsoil/src/vendor/configdb/")
sys.path.append("/opt/ofelia/AMsoil/src/")
sys.path.append("/opt/ofelia/AMsoil/src/vendor/virtrm")
import amconfigdb
import amconfigdbexceptions
import amsoil.core.pluginmanager as pm
pm.registerService("config", amconfigdb.ConfigDB())
pm.registerService("configexceptions", amconfigdbexceptions)
from models.resources.vtserver import VTServer
import unittest


class VMAllocatedSettersTest(unittest.TestCase):

    def given_this_vtserver(self):
        vtserver = VTServer()
        return vtserver

    def test_should_set_disc_space_gb(self):
        vtserver = self.given_this_vtserver()
        param = "set_disc_space_gb"
        vtserver.set_disc_space_gb(param)
        self.assertEquals(param, vtserver.disc_space_gb)

    def test_should_set_uuid(self):
        vtserver = self.given_this_vtserver()
        param = "set_uuid"
        vtserver.set_uuid(param)
        self.assertEquals(param, vtserver.uuid)

    def test_should_set_memory(self):
        vtserver = self.given_this_vtserver()
        param = "set_memory"
        vtserver.set_memory(param)
        self.assertEquals(param, vtserver.memory)

    def test_should_set_name(self):
        vtserver = self.given_this_vtserver()
        param = "set_name"
        vtserver.set_name(param)
        self.assertEquals(param, vtserver.name)

    def test_should_not_set_name(self):
        vtserver = self.given_this_vtserver()
        param = "//-not_set_name-//?"
        self.assertRaises(Exception, vtserver.set_name, param) 

    def test_should_set_number_of_cpus(self):
        vtserver = self.given_this_vtserver()
        param = "set_number_of_cpus"
        vtserver.set_number_of_cpus(param)
        self.assertEquals(param, vtserver.number_of_cpus)

    def test_should_set_available(self):
        vtserver = self.given_this_vtserver()
        param = "set_available"
        vtserver.set_available(param)
        self.assertEquals(param, vtserver.available)

    def test_should_set_enabled(self):
        vtserver = self.given_this_vtserver()
        param = "set_enabled"
        vtserver.set_enabled(param)
        self.assertEquals(param, vtserver.enabled)

    def test_should_set_cpu_frequency(self):
        vtserver = self.given_this_vtserver()
        param = "set_cpu_frequency"
        vtserver.set_cpu_frequency(param)
        self.assertEquals(param, vtserver.cpu_frequency)

    def test_should_set_virtualization_technology(self):
        vtserver = self.given_this_vtserver()
        param = "xen"
        vtserver.set_virtualization_technology(param)
        self.assertEquals(param, vtserver.virtualization_technology)

    def test_should_not_set_virtualization_technology_and_raise_exception(self):
        vtserver = self.given_this_vtserver()
        param = "set_virtualization_technology"
        self.assertRaises(Exception, vtserver.set_virtualization_technology, param)

    def test_should_set_operating_system_type(self):
        vtserver = self.given_this_vtserver()
        param = "GNU/Linux"
        vtserver.set_operating_system_type(param)
        self.assertEquals(param, vtserver.operating_system_type)

    def test_should_not_set_operating_system_type_and_raise_exception(self):
        vtserver = self.given_this_vtserver()
        param = "set_operating_system_type"
        self.assertRaises(Exception, vtserver.set_operating_system_type, param)

    def test_should_set_operating_system_version(self):
        vtserver = self.given_this_vtserver()
        param = "6.0"
        vtserver.set_operating_system_version(param)
        self.assertEquals(param, vtserver.operating_system_version)

    def test_should_not_set_operating_system_version_and_raise_exception(self):
        vtserver = self.given_this_vtserver()
        param = "set_operating_system_version"
        self.assertRaises(Exception, vtserver.set_operating_system_version, param)

    def test_should_set_operating_system_distribution(self):
        vtserver = self.given_this_vtserver()
        param = "Debian"
        vtserver.set_operating_system_distribution(param)
        self.assertEquals(param, vtserver.operating_system_distribution)

    def test_should_not_set_operating_system_distribution_and_raise_exception(self):
        vtserver = self.given_this_vtserver()
        param = "set_operating_system_distribution"
        self.assertRaises(Exception, vtserver.set_operating_system_distribution, param)

if __name__ == '__main__':
    unittest.main()

