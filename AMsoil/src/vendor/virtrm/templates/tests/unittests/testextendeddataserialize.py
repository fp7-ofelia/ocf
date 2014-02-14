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

class TestExtendedDataSerialize(unittest.TestCase):

    def given_this_ExtendedData_instance_serialized(self):
         ed = ExtendedData(True)
         for i in range(0,9):
             setattr(ed, "extension%i" % i, "value%i" % i)
         return ed.serialize()

    def test_should_deserialize(self):
        ed_serialized = self.given_this_ExtendedData_instance_serialized()
        ed  = ExtendedData.deserialize(ed_serialized)
        self.assertTrue(isinstance(ed, ExtendedData))
    
    def given_a_deserialized_instance(self):
        ed = ExtendedData(True)
        for i in range(0,4):
            setattr(ed, "extension%i" % i, "value%i" % i)
        ed_serialized = ed.serialize()
        return ExtendedData.deserialize(ed_serialized)

    def test_should_contain_extensions(self):
        ed = self.given_a_deserialized_instance()
        for i in range(0,4):
            self.assertEquals("value%i" % i, getattr(ed, "extension%i" % i))
 
if __name__ == '__main__':
    unittest.main()
