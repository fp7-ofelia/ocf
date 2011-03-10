from vt_manager.communication.utils.XmlUtils import *
from vt_manager.controller.Translator import Translator
from vt_manager.models import *
from vt_manager.controller.ProvisioningDispatcher import *
#from vt_manager.communication import *

s = xmlFileToString('../agent/utils/xml/query.xml')
r = XmlHelper.parseXmlString(s)
VMmodel = Translator.VMtoModel(r.query.provisioning.action[0].virtual_machine)
ProvisioningDispatcher.setVMinterfaces(VMmodel, r.query.provisioning.action[0].virtual_machine)
print VMmodel.getMacs()
print VMmodel.getMacs()[0].getMac()
