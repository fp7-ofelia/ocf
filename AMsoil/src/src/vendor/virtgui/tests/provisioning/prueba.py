import os
import sys
import uuid, random 
from os.path import dirname, join

PYTHON_DIR = join(dirname(__file__), '/opt/ofelia/vt_manager/src/python/')

# This is needed because wsgi disallows using stdout
sys.stdout = sys.stderr

os.environ['DJANGO_SETTINGS_MODULE'] = 'vt_manager.settings'

sys.path.insert(0,PYTHON_DIR)


from vt_manager.models.VTServer import VTServer
from vt_manager.communication.utils.XmlHelper import *
from vt_manager.communication.XmlRpcClient import XmlRpcClient
from vt_manager.communication.southCommInterface import *
rspec = XmlHelper.parseXmlString(xmlFileToString('createVM.xml'))
actionUUID = uuid.uuid4()
rspec.query.provisioning.action[0].id=actionUUID
rspec.query.provisioning.action[0].virtual_machine.uuid=uuid.uuid4()
rspec.query.provisioning.action[0].virtual_machine.name=random.randint(0,1000)

XmlRpcClient.callRPCMethodBasicAuth("https://192.168.254.193:8445/xmlrpc/plugin","expedient","expedient","send","https://expedient:expedient@192.168.254.193/vt_plugin/xmlrpc/vt_am/",XmlHelper.craftXmlClass(rspec))


#AGENT DEVUELVE ONGOING
#import time
#time.sleep(10)
#response = XmlHelper.parseXmlString(xmlFileToString('failresponse.xml'))
#response.response.provisioning.action[0].id=actionUUID
#response.response.provisioning.action[0].status="ONGOING"
#sendAsync(XmlHelper.craftXmlClass(response))
#
#
##AGENT DEVUELVE FAIL
#time.sleep(10)
#response = XmlHelper.parseXmlString(xmlFileToString('failresponse.xml'))
#response.response.provisioning.action[0].id=actionUUID
#sendAsync(XmlHelper.craftXmlClass(response))
