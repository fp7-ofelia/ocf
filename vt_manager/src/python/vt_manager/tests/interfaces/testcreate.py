from vt_manager.models import *
from vt_manager.communication.utils.XmlUtils import *
import xmlrpclib

am = xmlrpclib.Server('https://expedient:expedient@192.168.254.193:8445/xmlrpc/plugin')
xml = xmlFileToString('communication/utils/queryCreate.xml')
print xml
am.send("https://expedient:expedient@192.168.254.193/vt_plugin/xmlrpc/vt_am/",xml)





