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
def listResources(hashV, serverUUID = 'None', projectUUID = 'None', sliceUUID ='None'):

    logging.debug("Enter listResources")
    infoRspec = XmlHelper.getSimpleInformation()
     
    try:
        rHashObject =  resourcesHash.objects.get(serverUUID = serverUUID, projectUUID = projectUUID, sliceUUID = sliceUUID)
    except:
        rHashObject = resourcesHash(hashValue = -1, serverUUID = serverUUID, projectUUID= projectUUID, sliceUUID = sliceUUID)
        rHashObject.save()

    if hashV == rHashObject.hashValue:
        return hashV, ''

    else:

        if serverUUID != 'None':
            servers = VTServer.objects.filter(uuid = serverUUID)
        else:
            servers = VTServer.objects.all()
        
        if not servers:
            logging.debug("No VTServers available")
            infoRspec.response.information.resources.server.pop()
            listR = XmlHelper.craftXmlClass(infoRspec)
            hashV = hash(listR)

        sIndex = 0
        vIndex = 0
        for server in servers:
            #add Server 
            if(sIndex != 0):
                newServer = copy.deepcopy(infoRspec.response.information.resources.server[0])
                infoRspec.response.information.resources.server.append(newServer)
            
            Translator.ServerModelToClass(server, infoRspec.response.information.resources.server[sIndex] )
            if (projectUUID is not 'None'):
                vms = VM.objects.filter(serverID = server.uuid, projectId = projectUUID) 
            else:
                vms = VM.objects.filter(serverID = server.uuid)
            if not vms:
                logging.debug("No VMs available")
                if infoRspec.response.information.resources.server[sIndex].virtual_machine:
                    infoRspec.response.information.resources.server[sIndex].virtual_machine.pop()
            elif (sliceUUID is not 'None'):
                vms = vms.filter(sliceId = sliceUUID)
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
        
        listR =   XmlHelper.craftXmlClass(infoRspec)
        hashV = hash(listR)
        return hashV, listR

@rpcmethod(url_name="plugin")    
def ping(challenge):
    print "PINGING"
    return challenge
 
