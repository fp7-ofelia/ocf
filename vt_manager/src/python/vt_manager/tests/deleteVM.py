import os
import sys

#PYTHON_DIR = join(dirname(__file__), '/opt/ofelia/vt_manager/src/python/')
PYTHON_DIR = os.path.join(os.path.dirname(__file__), "../..")

# This is needed because wsgi disallows using stdout
sys.stdout = sys.stderr

os.environ['DJANGO_SETTINGS_MODULE'] = 'vt_manager.settings.settingsLoader'

sys.path.insert(0,PYTHON_DIR)

from vt_manager.models.VirtualMachine import VirtualMachine

vmid = str(sys.argv[1])

vm = VirtualMachine.objects.get(id = vmid).getChildObject()
server = vm.Server.get()
server.deleteVM(vm)
