import sys
sys.path.append("/opt/ofelia/AMsoil/src/src/plugins/configdb/")
sys.path.append("/opt/ofelia/AMsoil/src/src/")
sys.path.append("/opt/ofelia/AMsoil/src/src/vendor/virtrm")
import amconfigdb
import amconfigdbexceptions
import amsoil.core.pluginmanager as pm
pm.registerService("config", amconfigdb.ConfigDB())
pm.registerService("configexceptions", amconfigdbexceptions)
from templates.extendeddata import ExtendedData
import unittest

class TestExtendedData(unittest.TestCase):

    def given_this_extended_data_instance(self):
        return ExtendedData(track=False)
         
    def test_should_add_extension(self):
        ed = self.given_this_extended_data_instance()
        extension_name = "extensionA"
        extension_value = "valueA"
        ed.add_extension(extension_name,extension_value)
        self.assertEquals(extension_value, getattr(ed, extension_name))

    def test_should_get_extension(self):
        ed = self.given_this_extended_data_instance()
        extension_name = "extensionB"
        extension_value = "valueB"
        setattr(ed, extension_name, extension_value)
        self.assertEquals(extension_value, ed.get_extension(extension_name))

    def test_should_update_value(self):
        ed = self.given_this_extended_data_instance()
        extension_name = "extensionC"
        extension_value = "valC"
        extension_value_updated = "valueC"
        setattr(ed, extension_name, extension_value)
        ed.update_extension(extension_name, extension_value_updated)
        self.assertEquals(extension_value_updated, getattr(ed, extension_name))       

    def test_should_remove_extension(self):
        ed = self.given_this_extended_data_instance() 
        extension_name = "extensionD"
        extension_value = "valueD"
        setattr(ed, extension_name, extension_value)        
        ed.remove_extension(extension_name)
        self.assertRaises(AttributeError, getattr, ed, extension_name)
        
       
if __name__ == '__main__':
    unittest.main()

