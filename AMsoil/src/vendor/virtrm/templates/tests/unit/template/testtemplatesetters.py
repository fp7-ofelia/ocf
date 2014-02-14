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
import unittest


class TemplateSettersTest(unittest.TestCase):

    def given_this_template(self):
        template = Template()
        return template

    def test_set_description(self):
        template = self.given_this_template()
        param = "set_description"
        template.set_description(param)
        self.assertEquals(param, template.description)

    def test_set_do_save(self):
        template = self.given_this_template()
        param = "set_do_save"
        template.set_do_save(param)
        self.assertEquals(param, template.do_save)

    def test_set_extended_data(self):
        template = self.given_this_template()
        param = "set_extended_data"
        template.set_extended_data(param)
        self.assertEquals(param, template.extended_data)

    def test_set_hard_disk_origin_path(self):
        template = self.given_this_template()
        param = "set_hard_disk_origin_path"
        template.set_hard_disk_origin_path(param)
        self.assertEquals(param, template.hard_disk_origin_path)

    def test_set_hard_disk_setup_type(self):
        template = self.given_this_template()
        param = "set_hard_disk_setup_type"
        template.set_hard_disk_setup_type(param)
        self.assertEquals(param, template.hard_disk_setup_type)

    def test_set_img_file_url(self):
        template = self.given_this_template()
        param = "set_img_file_url"
        template.set_img_file_url(param)
        self.assertEquals(param, template.img_file_url)

    def test_set_name(self):
        template = self.given_this_template()
        param = "set_name"
        template.set_name(param)
        self.assertEquals(param, template.name)

    def test_set_operating_system_distribution(self):
        template = self.given_this_template()
        param = "set_operating_system_distribution"
        template.set_operating_system_distribution(param)
        self.assertEquals(param, template.operating_system_distribution)

    def test_set_operating_system_type(self):
        template = self.given_this_template()
        param = "set_operating_system_type"
        template.set_operating_system_type(param)
        self.assertEquals(param, template.operating_system_type)

    def test_set_operating_system_version(self):
        template = self.given_this_template()
        param = "set_operating_system_version"
        template.set_operating_system_version(param)
        self.assertEquals(param, template.operating_system_version)

    def test_set_virtualization_type(self):
        template = self.given_this_template()
        param = "set_virtualization_type"
        template.set_virtualization_type(param)
        self.assertEquals(param, template.virtualization_type)

    def test_set_virtualization_technology(self):
        template = self.given_this_template()
        param = "set_virtualization_technology"
        template.set_virtualization_technology(param)
        self.assertEquals(param, template.virtualization_technology)

if __name__ == '__main__':
    unittest.main()
