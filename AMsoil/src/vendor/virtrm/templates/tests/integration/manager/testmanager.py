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

class TestTemplateManager(unittest.TestCase):

   def setUp(self):
       self.given_the_following_templates()
       self.given_the_following_manager()

   def tearDown(self):
       db.session.query(Template).filter_by(uuid=self.template_a.get_uuid()).delete()
       db.session.query(Template).filter_by(uuid=self.template_b.get_uuid()).delete()
       self.template_a = None
       self.template_b = None
       self.manager = None

   def given_the_following_two_templates(self):
       self.params_a = ["nameA","descriptionA","os_typeA","os_versionA","os_distroA","virt_setup_typeA","hd_setup_typeA","hd_pathA","extended_dataA","img_urlA","virt_techA" ,False]
       self.params_b = ["nameB","descriptionB","os_typeB","os_versionB","os_distroB","virt_setup_typeB","hd_setup_typeB","hd_pathB","extended_dataB","img_urlB","virt_techB" ,False]
       self.template_a = Template(*params_a)
       self.template_b = Template(*params_b)
 
    def given_the_following_manager(self):
        self.manager = TemplateManager()    

    def test_should_add_templates(self):
        pass 
        
    def test_should_get_template_by_filtering_template_params(self):
        pass

    def test_should_delete_template(self):
       pass

    def test_should_edit_template(self):
       pass

    def test_should_get_all_templates(self):
       pass





