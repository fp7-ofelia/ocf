import sys
sys.path.append("/opt/ofelia/AMsoil/src/plugins/configdb/")
sys.path.append("/opt/ofelia/AMsoil/src/")
sys.path.append("/opt/ofelia/AMsoil/src/vendor/virtrm")
import amconfigdb
import amconfigdbexceptions
import amsoil.core.pluginmanager as pm
pm.registerService("config", amconfigdb.ConfigDB())
pm.registerService("configexceptions", amconfigdbexceptions)
from templates.template import Template
from templates.extendeddata import ExtendedData
import unittest

class TestTemplateSerialization(unittest.TestCase):

     def given_raw_template(self):
         return Template()

     def test_should_add_extension(self):
         template = self.given_raw_template()
         extension = "extension"
         value = "value"
         template.add_extension(extension, value)
         self.assertEquals(value, getattr(template.extended_data_manager, extension))
 
     def given_a_template_including_extended_data(self):
         ed = ExtendedData()
         ed.add_extension("extension","value")
         serial = ed.serialize()
         return Template(extended_data=serial)

     def test_should_load_extension_manager(self):
         t = self.given_a_template_including_extended_data()
         self.assertTrue(isinstance(t.extended_data_manager, ExtendedData))

     def test_should_dump_extensions(self):
         t = self.given_a_template_including_extended_data()
         self.assertEquals("extension : value\n", t.get_extended_data())


if __name__ == '__main__':
    unittest.main()

