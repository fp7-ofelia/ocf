import os
import sys
from os.path import dirname, join
from django.conf import *

#configobj
try:
        from configobj import ConfigObj
except:
        #FIXME: ugly
        os.system("apt-get update && apt-get install python-configobj -y")
        from configobj import ConfigObj


PYTHON_DIR = join(dirname(__file__), '../../../../../../src/python')

# This is needed because wsgi disallows using stdout
sys.stdout = sys.stderr

os.environ['DJANGO_SETTINGS_MODULE'] = 'vt_manager.settings.settingsLoader'

sys.path.insert(0,PYTHON_DIR)

from vt_manager.settings.settingsLoader import XMLRPC_USER, XMLRPC_PASS
from vt_manager.models import VirtualMachine

print "Updating VM's callback URLs to use XMLRPC user in the database..."
for vm in VirtualMachine.objects.all():
	url = vm.getCallBackURL()
	url= url[:url.find('//')+2]+XMLRPC_USER+":"+XMLRPC_PASS+url[url.find('@'):]
	vm.setCallBackURL(url)
	vm.save()

