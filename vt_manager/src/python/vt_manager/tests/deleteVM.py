import os
import sys
from os.path import dirname, join

PYTHON_DIR = join(dirname(__file__), '/opt/ofelia/vt_manager/src/python/')

# This is needed because wsgi disallows using stdout
sys.stdout = sys.stderr

os.environ['DJANGO_SETTINGS_MODULE'] = 'vt_manager.settings.settingsLoader'

sys.path.insert(0,PYTHON_DIR)


from vt_manager.models.VirtualMachine import VirtualMachine

vmName = str(sys.argv[1])

vm = VirtualMachine.objects.get(name = vmName).getChildObject()
server = vm.Server.get()
server.deleteVM(vm)
