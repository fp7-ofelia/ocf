import os
import sys
from os.path import dirname, join

PYTHON_DIR = join(dirname(__file__), '/opt/ofelia/expedient/src/python/')

# This is needed because wsgi disallows using stdout
sys.stdout = sys.stderr

sys.path.insert(0, PYTHON_DIR)
from expedient.clearinghouse import settings
#os.environ['DJANGO_SETTINGS_MODULE'] = 'expedient.clearinghouse.settings'

sys.path.insert(0, "/opt/ofelia/expedient/src/python/plugins/")
from vt_plugin.models import *

vms = VM.objects.all()
for vm in vms:
	server = VTServer.objects.get(uuid = vm.serverID)
	server.vms.remove(vm)
	vm.completeDelete()
