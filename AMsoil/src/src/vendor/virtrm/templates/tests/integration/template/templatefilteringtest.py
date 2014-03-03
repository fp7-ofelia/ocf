import sys
sys.path.append("/opt/ofelia/AMsoil/src/plugins/virtconfigdb/")
sys.path.append("/opt/ofelia/AMsoil/src/")
sys.path.append("/opt/ofelia/AMsoil/src/vendor/virtrm")
import amconfigdb
import amconfigdbexceptions
import amsoil.core.pluginmanager as pm
pm.registerService("config", amconfigdb.ConfigDB())
pm.registerService("configexceptions", amconfigdbexceptions)
from templates.template import Template
import amsoil.core.pluginmanager as pm
import unittest
config = pm.getService("config")
from utils.base import set_up as SETUP
from utils.base import drop_table as DROP_TABLE
from utils.base import db 
import time

#DROP_TABLE()
SETUP()

class TemplateFilteringTest(unittest.TestCase):

   def setUp(self):
       self.given_a_template_table()

   def tearDown(self):
       db.session.query(Template).filter_by(uuid=self.uuid).delete()
              
  
   def given_a_template_table(self):
      params = ["name","description","os_type","os_version","os_distro","virt_setup_type","hd_setup_type","hd_path","extended_data","img_url","virt_tech" ,True]
      self.expected_template = Template(*params)
      self.uuid = self.expected_template.get_uuid()

   def test_should_query_template_instances(self):
      t = db.session.query(Template)
      self.assertTrue(isinstance(t[0],Template))

   def test_should_retrieve_template_by_uuid(self):
      t = db.session.query(Template).filter_by(uuid=self.uuid).one()
      self.assertEquals(self.expected_template, t)

   def test_should_retrieve_template_by_name(self):
      t = db.session.query(Template).filter_by(name=self.expected_template.get_name()) 
      t = t.filter_by(uuid=self.uuid).one() 
      self.assertEquals(self.expected_template, t)

   def test_should_retrieve_template_by_description(self):
      t = db.session.query(Template).filter_by(description=self.expected_template.get_description())
      t = t.filter_by(uuid=self.uuid).one()
      self.assertEquals(self.expected_template, t)

   def test_should_retrieve_template_by_operating_system_type(self):
      t = db.session.query(Template).filter_by(operating_system_type=self.expected_template.get_operating_system_type())
      t = t.filter_by(uuid=self.uuid).one()
      self.assertEquals(self.expected_template, t)

   def test_should_retrieve_template_by_operating_system_distribution(self):
      t = db.session.query(Template).filter_by(operating_system_distribution=self.expected_template.get_operating_system_distribution())
      t = t.filter_by(uuid=self.uuid).one()
      self.assertEquals(self.expected_template, t)

   def test_should_retrieve_template_by_operating_system_version(self):
      t = db.session.query(Template).filter_by(operating_system_version=self.expected_template.get_operating_system_version())
      t = t.filter_by(uuid=self.uuid).one()
      self.assertEquals(self.expected_template, t)

   def test_should_retrieve_template_by_hard_disk_setup_type(self):
      t = db.session.query(Template).filter_by(hard_disk_setup_type=self.expected_template.get_hard_disk_setup_type())
      t = t.filter_by(uuid=self.uuid).one()
      self.assertEquals(self.expected_template, t)

   def test_should_retrieve_template_by_hard_disk_origin_path(self):
      t = db.session.query(Template).filter_by(hard_disk_origin_path=self.expected_template.get_hard_disk_origin_path())
      t = t.filter_by(uuid=self.uuid).one()
      self.assertEquals(self.expected_template, t)

   def test_should_retrieve_template_by_virtualization_technology(self):
      t = db.session.query(Template).filter_by(virtualization_technology=self.expected_template.get_virtualization_technology())
      t = t.filter_by(uuid=self.uuid).one()
      self.assertEquals(self.expected_template, t)

   def test_should_retrieve_template_by_virtualization_type(self):
      t = db.session.query(Template).filter_by(virtualization_type=self.expected_template.get_virtualization_type())
      t = t.filter_by(uuid=self.uuid).one()
      self.assertEquals(self.expected_template, t)

if __name__ == '__main__':
    unittest.main()  
