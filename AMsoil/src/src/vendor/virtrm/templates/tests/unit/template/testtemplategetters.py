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
import unittest
from utils.base import db

class TemplateGettersTest(unittest.TestCase):

    def given_this_template(self):
        template = Template()
        return template

    def test_get_description(self):
        template = self.given_this_template()
        param = "get_description"
        template.description = param
        self.assertEquals(param, template.get_description())

    def test_get_do_save(self):
        template = self.given_this_template()
        param = "do_save"
        template.do_save = param
        self.assertEquals(param, template.get_do_save())

    def test_get_extended_data(self):
        template = self.given_this_template()
        param = "get_extended_data"
        template.extended_data = param
        self.assertEquals(param, template.get_extended_data())

    def test_get_hard_disk_origin_path(self):
        template = self.given_this_template()
        param = "get_hard_disk_origin_path"
        template.hard_disk_origin_path = param
        self.assertEquals(param, template.get_hard_disk_origin_path())

    def test_get_hard_disk_setup_type(self):
        template = self.given_this_template()
        param = "get_hard_disk_setup_type"
        template.hard_disk_setup_type = param
        self.assertEquals(param, template.get_hard_disk_setup_type())

    def test_get_img_file_url(self):
        template = self.given_this_template()
        param = "get_img_file_url"
        template.img_file_url = param
        self.assertEquals(param, template.get_img_file_url())

    def test_get_name(self):
        template = self.given_this_template()
        param = "get_name"
        template.name = param
        self.assertEquals(param, template.get_name())

    def test_get_operating_system_distribution(self):
        template = self.given_this_template()
        param = "get_operating_system_distribution"
        template.operating_system_distribution = param
        self.assertEquals(param, template.get_operating_system_distribution())

    def test_get_operating_system_type(self):
        template = self.given_this_template()
        param = "get_operating_system_type"
        template.operating_system_type = param
        self.assertEquals(param, template.get_operating_system_type())

    def test_get_operating_system_version(self):
        template = self.given_this_template()
        param = "get_operating_system_version"
        template.operating_system_version = param
        self.assertEquals(param, template.get_operating_system_version())

    def test_get_virtualization_type(self):
        template = self.given_this_template()
        param = "get_virtualization_type"
        template.virtualization_type = param
        self.assertEquals(param, template.get_virtualization_type())

    def test_get_virtualization_technology(self):
        template = self.given_this_template()
        param = "get_virtualization_technology"
        template.virtualization_technology = param
        self.assertEquals(param, template.get_virtualization_technology())

    def test_should_be_eqauals(self):
        template = self.given_this_template()
        template2 = self.given_this_template()
        template2.uuid = template.get_uuid()
        self.assertEquals(template, template)

if __name__ == '__main__':
    unittest.main()
