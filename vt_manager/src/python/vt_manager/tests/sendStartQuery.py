#!/usr/bin/python
from vt_manager.models import *
from vt_manager.communication.utils.XmlUtils import *
import xmlrpclib
from vt_manager.controller.utils.Translator import Translator
from vt_manager.controller.dispatchers.ProvisioningDispatcher import ProvisioningDispatcher
''' Argument checking '''
def checkArgs():
    if(len(sys.argv) != 1): #one
        raise Exception("Illegal number of arguments\n\n")



#def main():
def main(uuid):

    #checkArgs()
    
    #ag = xmlrpclib.Server('https://84.88.40.12:9229/')
    
    rspec = XmlHelper.parseXmlString(xmlFileToString('communication/utils/xml/queryStart.xml'))
    
    #Translator.PopulateNewAction(rspec.query.provisioning.action[0], VM.objects.get(uuid = sys.argv[1]))
    Translator.PopulateNewAction(rspec.query.provisioning.action[0], VM.objects.get(uuid = uuid))
    
    #ag.send("https://expedient:expedient@147.83.206.92:8445/xmlrpc/agent",1, "hfw9023jf0sdjr0fgrbjk",XmlHelper.craftXmlClass(rspec))
    ProvisioningDispatcher.processProvisioning(rspec.query.provisioning)
    
#Calling main
if __name__ == "__main__":
    main()


