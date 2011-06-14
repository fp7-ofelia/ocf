from vt_manager.models import *
from vt_manager.communication.utils.XmlUtils import *
import xmlrpclib

am = xmlrpclib.Server('https://expedient:expedient@192.168.254.193:8445/xmlrpc/agent')
xml = xmlFileToString('communication/utils/queryStart2.xml')

am.send(xml)




