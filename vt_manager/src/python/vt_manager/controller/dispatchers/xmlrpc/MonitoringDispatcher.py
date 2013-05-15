from vt_manager.controller.actions.ActionController import ActionController
from vt_manager.controller.drivers.VTDriver import VTDriver
import xmlrpclib, threading, logging, copy
from vt_manager.communication.utils.XmlHelper import XmlHelper
from vt_manager.models.resourcesHash import resourcesHash


class MonitoringDispatcher():


	@staticmethod
	def getStoredStatistics():

		logging.debug("Enter StoredStatistics")
		infoRspec = XmlHelper.getEmptyStaticsMonitoringResponse()
		servers = VTDriver.getAllServers()
		baseServer = copy.deepcopy(infoRspec.response.information.resources.server[0].virtual_machine[0]

)
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
	
				InformationDispatcher.__ServerModelToClass(server, infoRspec.response.information.resources.server[sIndex] )
				if (projectUUID is not 'None'):
					vms = server.getVMs(projectId = projectUUID)
				else:
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
					InformationDispatcher.__VMmodelToClass(vm, infoRspec.response.information.resources.server[sIndex].virtual_machine[vIndex])
	
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
	
