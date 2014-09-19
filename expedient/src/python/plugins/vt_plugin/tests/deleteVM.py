import os
import sys

# This is needed because wsgi disallows using stdout
sys.stdout = sys.stderr

# Add OCF's python files directory to system path, using a relative path from current file
#PYTHON_DIR = os.path.join(os.path.dirname(__file__), '/opt/ofelia/expedient/src/python/')
PYTHON_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../..")
#PLUGINS_DIR = os.path.join(os.path.dirname(__file__), '/opt/ofelia/expedient/src/python/plugins')
PLUGINS_DIR = os.path.join(PYTHON_DIR, "plugins")

os.environ['DJANGO_SETTINGS_MODULE'] = 'expedient.clearinghouse.settings'
sys.path.insert(0,PLUGINS_DIR)
sys.path.insert(0,PYTHON_DIR)

from vt_plugin.models import *

vmid = str(sys.argv[1])
vm = VM.objects.get(id = vmid)
server = VTServer.objects.get(uuid = vm.serverID)
server.vms.remove(vm)
vm.completeDelete()

