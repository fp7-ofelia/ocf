import sys
sys.path.append("/opt/ofelia/AMsoil/src/plugins/configdb/")
sys.path.append("/opt/ofelia/AMsoil/src/")
sys.path.append("/opt/ofelia/AMsoil/src/vendor/virtrm")
import amconfigdb
import amconfigdbexceptions
import amsoil.core.pluginmanager as pm
pm.registerService("config", amconfigdb.ConfigDB())
pm.registerService("configexceptions", amconfigdbexceptions)
from templates.extendeddata import ExtendedData
import unittest

class TestExtendedDataTrack(unittest.TestCase):

    def given_this_extended_data_instance(self):
        return ExtendedData(True)

    def test_should_append_extensions(self):
        ed = self.given_this_extended_data_instance()
        extension_name = "extension"
        ed.append_extension_list(extension_name)
        self.assertEquals(extension_name, ed.extensions[0])
  
    def test_should_remove_extensions(self):
        ed = self.given_this_extended_data_instance()
        extension_name = "extension0"
        ed.extensions.append(extension_name)
        ed.remove_extension_list(extension_name)
        self.assertEquals(0, len(ed.extensions)) 

    def test_should_add_extension_to_the_list(self):
        ed = self.given_this_extended_data_instance()
        extension_name = "extensionA"
        extension_value = "valueA"
        ed.add_extension(extension_name, extension_value)
        self.assertEquals(extension_name, ed.extensions[0])

    def test_should_remove_extensions_to_the_list(self):
        ed = self.given_this_extended_data_instance()
        extension_name = "extensionB"
        extension_value = "valueB"
        ed.remove_extension(extension_name, extension_value)
        self.assertEquals(0, len(ed.extensions))

if __name__ == '__main__':
    unittest.main()
