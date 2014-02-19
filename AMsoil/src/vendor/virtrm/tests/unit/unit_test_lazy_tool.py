import sys
sys.path.append("/opt/ofelia/AMsoil/src/vendor/configdb/")
sys.path.append("/opt/ofelia/AMsoil/src/")
sys.path.append("/opt/ofelia/AMsoil/src/vendor/virtrm/")
import amconfigdb
import amconfigdbexceptions
import amsoil.core.pluginmanager as pm
pm.registerService("config", amconfigdb.ConfigDB())
pm.registerService("configexceptions", amconfigdbexceptions)

from models.resources.vmallocated import VMAllocated

vm = VMAllocated()

diss = dir(vm)

def get_header(className):
    header = '''
import sys
sys.path.append("/opt/ofelia/AMsoil/src/vendor/configdb/")
sys.path.append("/opt/ofelia/AMsoil/src/")
sys.path.append("/opt/ofelia/AMsoil/src/vendor/virtrm")
import amconfigdb
import amconfigdbexceptions
import amsoil.core.pluginmanager as pm
pm.registerService("config", amconfigdb.ConfigDB())
pm.registerService("configexceptions", amconfigdbexceptions)
from models.resources.vmallocated import VMAllocated
import unittest\n\n
class %s(unittest.TestCase):\n\n''' %( className)

    return header

def get_tail():
    tail = '''if __name__ == '__main__':
    unittest.main()\n'''
    return tail

def get_main_method():
    main_method  = '''    def given_this_vm(self):
        vm_allocated = VMAllocated()
        return vm_allocated\n\n'''
    return main_method

def get_test_method(method):
    method_struct = "    def test_should_%s(self):" % method
    body = '''
        vm_allocated = self.given_this_vm()
        param = "template"
        vm_allocated.%s = param
        self.assertEquals(param, vm_allocated.%s())\n\n''' %( method[4:],method)
    return method_struct + body

def main():

    strings = get_header("VMAllocatedSettersTest")
    strings += get_main_method()
    print strings
    methods = dir(VMAllocated())
    for method in methods:
        print method
        if method.startswith("set_"):
           strings += get_test_method(method)

    strings += get_tail()
    return strings

print main()
 



