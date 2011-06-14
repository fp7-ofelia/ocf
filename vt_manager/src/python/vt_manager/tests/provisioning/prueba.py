import os
import sys
from os.path import dirname, join

PYTHON_DIR = join(dirname(__file__), '/opt/ofelia/vt_manager/src/python/')

# This is needed because wsgi disallows using stdout
sys.stdout = sys.stderr

os.environ['DJANGO_SETTINGS_MODULE'] = 'vt_manager.settings'

sys.path.insert(0,PYTHON_DIR)


from vt_manager.models.VTServer import VTServer
from vt_manager.communication.utils.XmlHelper import *
from vt_manager.communication.XmlRpcClient import XmlRpcClient

XmlRpcClient.callRPCMethodBasicAuth("https://192.168.254.193:8445/xmlrpc/plugin","expedient","expedient","send","https://expedient:expedient@192.168.254.193/vt_plugin/xmlrpc/vt_am/",xmlFileToString('createVM.xml'))
