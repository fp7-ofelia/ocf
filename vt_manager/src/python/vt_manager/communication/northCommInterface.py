from django.http import *
import os, logging
import sys
from vt_manager.models import *
from vt_manager.controller import *
from vt_manager.controller.dispatchers.DispatcherLauncher import *
from vt_manager.communication.utils.XmlUtils import *
from vt_manager.utils.ServiceThread import *
from vt_manager.common.rpc4django import rpcmethod
from vt_manager.common.rpc4django import *
import copy
from threading import Thread

@rpcmethod(url_name="plugin")
#def send(callBackUrl, expID, xml):
def send(callBackUrl, xml):
    try:
        logging.debug("XML RECEIVED: \n%s" % xml)
        rspec = XmlHelper.parseXmlString(xml)
    except Exception as e:
        logging.error("send() could not parse\n")
        logging.error(e)
        return
    ServiceThread.startMethodInNewThread(processXmlQuery ,rspec, url = callBackUrl)
    return

@rpcmethod(url_name="plugin")
def listResources(serverName = 'None', projectName = 'None', sliceName ='None'):

    logging.debug("Enter listResources")
    infoRspec = XmlHelper.getSimpleInformation()
    #cleanInfoRspec
    
    if serverName is not 'None':
        servers = VTServer.objects.filter(name = serverName)
    else:
        servers = VTServer.objects.all()
    
    if not servers:
        logging.error("No VTServers available")
        infoRspec.response.information.resources.server.pop()
        return XmlHelper.craftXmlClass(infoRspec)
    sIndex = 0
    vIndex = 0
    for server in servers:
        #add Server 
        if(sIndex != 0):
            newServer = copy.deepcopy(infoRspec.response.information.resources.server[0])
            infoRspec.response.information.resources.server.append(newServer)

        Translator.ServerModelToClass(server, infoRspec.response.information.resources.server[sIndex] )
        if (projectName is not 'None'):
            vms = VM.objects.filter(serverID = server.name, project = projectName) 
        else:
            vms = VM.objects.filter(serverID = server.name)
        if not vms:
            logging.error("No VMs available")
            infoRspec.response.information.resources.server[sIndex].virtual_machine.pop()
        elif (sliceName is not 'None'):
            vms = vms.filter(sliceId = sliceName)
            if not vms:
                logging.error("No VMs available")
                infoRspec.response.information.resources.server[sIndex].virtual_machine.pop()
        for vm in vms:
            if (vIndex != 0):
                newVM = copy.deepcopy(infoRspec.response.information.resources.server[sIndex].virtual_machine[0])
                infoRspec.response.information.resources.server[sIndex].virtual_machine.append(newVM)
            
            Translator.VMmodelToClass(vm, infoRspec.response.information.resources.server[sIndex].virtual_machine[vIndex])
            vIndex = vIndex + 1
        sIndex = sIndex + 1
        
    logging.debug(infoRspec)
    return XmlHelper.craftXmlClass(infoRspec)
    

 
