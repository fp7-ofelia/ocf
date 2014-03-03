import sys
sys.path.append("/opt/ofelia/AMsoil/src/src/plugins/configdb/")
sys.path.append("/opt/ofelia/AMsoil/src/src/")
sys.path.append("/opt/ofelia/AMsoil/src/src/vendor/virtrm")
import amconfigdb
import amconfigdbexceptions
import amsoil.core.pluginmanager as pm
pm.registerService("config", amconfigdb.ConfigDB())
pm.registerService("configexceptions", amconfigdbexceptions)

from templates.template import Template

temp = Template()

diss = dir(temp)

def get_header(className):
    header = '''
import sys
sys.path.append("/opt/ofelia/AMsoil/src/src/plugins/configdb/")
sys.path.append("/opt/ofelia/AMsoil/src/src/")
sys.path.append("/opt/ofelia/AMsoil/src/src/vendor/virtrm")
import amconfigdb
import amconfigdbexceptions
import amsoil.core.pluginmanager as pm
pm.registerService("config", amconfigdb.ConfigDB())
pm.registerService("configexceptions", amconfigdbexceptions)
from templates.template import Template
import unittest\n\n
class %s(unittest.TestCase):\n\n''' %( className)

    return header

def get_tail():
    tail = '''if __name__ == '__main__':
    unittest.main()\n'''
    return tail

def get_main_method():
    main_method  = '''    def given_this_template(self):
        template = Template()
        return template\n\n'''
    return main_method

def get_test_method(method):
    method_struct = "    def test_%s(self):" % method
    body = '''
        template = self.given_this_template()
        param = "template"
        template.%s = param
        self.assertEquals(param, template.%s())\n\n''' %( method[4:],method)
    return method_struct + body

def main():

    strings = get_header("TemplateSettersTest")
    strings += get_main_method()
    print strings
    methods = dir(Template())
    for method in methods:
        print method
        if method.startswith("get_"):
           strings += get_test_method(method)

    strings += get_tail()
    return strings

print main()
 



