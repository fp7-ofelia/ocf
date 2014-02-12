import random
import unittest



class TemplateFields(unittest.TestCase):
    ''' Tests that all Template model fields are correctly set '''

    def given_this_template(self):
        ''' fill the template '''
        template = None
        return template

    def test_should_set_name(self):
        template = self.given_this_template()
        name = "template"
        template.set_name(name)
        self.assertEquals(name, template.name)

   def test_should_set_description(self):
        template = self.given_this_template()
        desc = "template"
        template.set_description()
        self.assertEquals(name, template.name)

   def test_should_set_name(self):
        template = self.given_this_template()
        name = "template"
        self.assertEquals(name, template.name)

   def test_should_set_name(self):
        template = self.given_this_template()
        name = "template"
        self.assertEquals(name, template.name)

   def test_should_set_name(self):
        template = self.given_this_template()
        name = "template"
        self.assertEquals(name, template.name)

   def test_should_set_name(self):
        template = self.given_this_template()
        name = "template"
        self.assertEquals(name, template.name)

   def test_should_set_name(self):
        template = self.given_this_template()
        name = "template"
        self.assertEquals(name, template.name)



if __name__ == '__main__':
    unittest.main()
