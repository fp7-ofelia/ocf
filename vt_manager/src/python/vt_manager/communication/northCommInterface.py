from django.http import *
import os, logging
import sys
from vt_manager.models import *
from vt_manager.controller import *
from vt_manager.controller.dispatchers.xmlrpc.DispatcherLauncher import DispatcherLauncher
from vt_manager.communication.utils.XmlHelper import *
from vt_manager.utils.ServiceThread import *
from vt_manager.common.rpc4django import rpcmethod
from vt_manager.common.rpc4django import *
import copy
from threading import Thread

from vt_manager.controller.drivers.VTDriver import VTDriver
from vt_manager.controller.dispatchers.xmlrpc.utils.Translator import Translator

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
	print "[LEODEBUG] XML"
	print xml
	ServiceThread.startMethodInNewThread(DispatcherLaucher.processXmlQuery ,rspec, url = callBackUrl)
	return

#@rpcmethod(url_name="plugin")
#def listResources(remoteHashValue, projectUUID = 'None', sliceUUID ='None'):
#
#    logging.debug("Enter listResources")
#    infoRspec = XmlHelper.getSimpleInformation()
#    servers = VTServer.objects.all()
#    baseVM = copy.deepcopy(infoRspec.response.information.resources.server[0].virtual_machine[0])
#    if not servers:
#        logging.debug("No VTServers available")
#        infoRspec.response.information.resources.server.pop()
#        resourcesString = XmlHelper.craftXmlClass(infoRspec)
#        localHashValue = str(hash(resourcesString))
#    else:
#        for sIndex, server in enumerate(servers):
#            if(sIndex == 0):
#                baseServer = copy.deepcopy(infoRspec.response.information.resources.server[0])
#            if(sIndex != 0):
#                newServer = copy.deepcopy(baseServer)
#                infoRspec.response.information.resources.server.append(newServer)
#
#            Translator.ServerModelToClass(server, infoRspec.response.information.resources.server[sIndex] )
#            if (projectUUID is not 'None'):
#                vms = VM.objects.filter(serverID = server.uuid, projectId = projectUUID)
#            else:
#                vms = VM.objects.filter(serverID = server.uuid)
#            if not vms:
#                logging.debug("No VMs available")
#                if infoRspec.response.information.resources.server[sIndex].virtual_machine:
#                    infoRspec.response.information.resources.server[sIndex].virtual_machine.pop()
#            elif (sliceUUID is not 'None'):
#                vms = vms.filter(sliceId = sliceUUID)
#                if not vms:
#                    logging.error("No VMs available")
#                    infoRspec.response.information.resources.server[sIndex].virtual_machine.pop()
#            for vIndex, vm in enumerate(vms):
#                if (vIndex != 0):
#                    newVM = copy.deepcopy(baseVM)
#                    infoRspec.response.information.resources.server[sIndex].virtual_machine.append(newVM)
#                Translator.VMmodelToClass(vm, infoRspec.response.information.resources.server[sIndex].virtual_machine[vIndex])
#
#        resourcesString =   XmlHelper.craftXmlClass(infoRspec)
#        localHashValue = str(hash(resourcesString))
#    
#    try:
#        rHashObject =  resourcesHash.objects.get(projectUUID = projectUUID, sliceUUID = sliceUUID)
#        rHashObject.hashValue = localHashValue
#        rHashObject.save()
#    except:
#        rHashObject = resourcesHash(hashValue = localHashValue, projectUUID= projectUUID, sliceUUID = sliceUUID)
#        rHashObject.save()
#    
#    if remoteHashValue == rHashObject.hashValue:
#        return localHashValue, ''
#    else:
#        return localHashValue, resourcesString


@rpcmethod(url_name="plugin")    
def ping(challenge):
	return challenge


@rpcmethod(url_name="plugin")
def listResources(remoteHashValue, projectUUID = 'None', sliceUUID ='None'):

	logging.debug("Enter listResources")
	infoRspec = XmlHelper.getSimpleInformation()
	print XmlHelper.craftXmlClass(infoRspec)
	#servers = VTServer.objects.all()
	servers = VTDriver.getAllServers()
	baseVM = copy.deepcopy(infoRspec.response.information.resources.server[0].virtual_machine[0])
	if not servers:
		logging.debug("No VTServers available")
		infoRspec.response.information.resources.server.pop()
		resourcesString = XmlHelper.craftXmlClass(infoRspec)
		localHashValue = str(hash(resourcesString))
	else:
		for sIndex, server in enumerate(servers):
			if(sIndex == 0):
				baseServer = copy.deepcopy(infoRspec.response.information.resources.server[0])
			if(sIndex != 0):
				newServer = copy.deepcopy(baseServer)
				infoRspec.response.information.resources.server.append(newServer)

			Translator.ServerModelToClass(server, infoRspec.response.information.resources.server[sIndex] )
			if (projectUUID is not 'None'):
				#vms = VM.objects.filter(serverID = server.uuid, projectId = projectUUID)
				vms = server.getVMs(projectId = projectUUID)
			else:
				#vms = VM.objects.filter(serverID = server.uuid)
				vms = server.getVMs()
			if not vms:
				logging.debug("No VMs available")
				if infoRspec.response.information.resources.server[sIndex].virtual_machine:
					infoRspec.response.information.resources.server[sIndex].virtual_machine.pop()
			elif (sliceUUID is not 'None'):
				vms = vms.filter(sliceId = sliceUUID)
				if not vms:
					logging.error("No VMs available")
					infoRspec.response.information.resources.server[sIndex].virtual_machine.pop()
			for vIndex, vm in enumerate(vms):
				if (vIndex != 0):
					newVM = copy.deepcopy(baseVM)
					infoRspec.response.information.resources.server[sIndex].virtual_machine.append(newVM)
				Translator.VMmodelToClass(vm, infoRspec.response.information.resources.server[sIndex].virtual_machine[vIndex])

		resourcesString =   XmlHelper.craftXmlClass(infoRspec)
		localHashValue = str(hash(resourcesString))

	try:
		rHashObject =  resourcesHash.objects.get(projectUUID = projectUUID, sliceUUID = sliceUUID)
		rHashObject.hashValue = localHashValue
		rHashObject.save()
	except:
		rHashObject = resourcesHash(hashValue = localHashValue, projectUUID= projectUUID, sliceUUID = sliceUUID)
		rHashObject.save()

	if remoteHashValue == rHashObject.hashValue:
		return localHashValue, ''
	else:
		return localHashValue, resourcesString
 
