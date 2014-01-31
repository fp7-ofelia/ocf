from vt_manager.controller.actions.ActionController import ActionController
from vt_manager.controller.drivers.VTDriver import VTDriver
import xmlrpclib, threading, logging, copy
from vt_manager.communication.utils.XmlHelper import XmlHelper
from vt_manager.models.resourcesHash import resourcesHash

class InformationDispatcher():

	@staticmethod
	def listResources(remoteHashValue, projectUUID = 'None', sliceUUID ='None'):
		logging.debug("Enter listResources")
		infoRspec = XmlHelper.getSimpleInformation()
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

	@staticmethod
	def listVMTemplatesInfo(serverUUID):
	#def listVMTemplatesInfo(serverUUID, callbackURL):
		logging.debug("Enter listVMTemplatesInfo")
		server = VTDriver.getServerByUUID(serverUUID)
		xmlrpc_server = xmlrpclib.Server(server.getAgentURL())
		templates_info = xmlrpc_server.list_vm_templates(server.getAgentPassword())
		#templates_info = xmlrpc_server.list_vm_templates(callbackURL, server.getAgentPassword())
		return str(templates_info)

	@staticmethod
	def __ServerModelToClass(sModel, sClass ):
		sClass.name = sModel.getName()
		#XXX: CHECK THIS
		sClass.id = sModel.id
		sClass.uuid = sModel.getUUID()
		sClass.operating_system_type = sModel.getOSType()
		sClass.operating_system_distribution = sModel.getOSDistribution()
		sClass.operating_system_version = sModel.getOSVersion()
		sClass.virtualization_type = sModel.getVirtTech()
		ifaces = sModel.getNetworkInterfaces()
		for ifaceIndex, iface in enumerate(ifaces):
			if ifaceIndex != 0:
				newInterface = copy.deepcopy(sClass.interfaces.interface[0])
				sClass.interfaces.interface.append(newInterface)
			if iface.isMgmt:
				sClass.interfaces.interface[ifaceIndex].ismgmt = True
			else:
				sClass.interfaces.interface[ifaceIndex].ismgmt = False
			sClass.interfaces.interface[ifaceIndex].name = iface.name   
			sClass.interfaces.interface[ifaceIndex].switch_id= iface.switchID   
			sClass.interfaces.interface[ifaceIndex].switch_port = iface.port  
 
	@staticmethod
	def __VMmodelToClass(VMmodel, VMxmlClass):

		VMxmlClass.name = VMmodel.getName()
		VMxmlClass.uuid = VMmodel.getUUID()
		VMxmlClass.status = VMmodel.getState()
		VMxmlClass.project_id = VMmodel.getProjectId()
		VMxmlClass.slice_id = VMmodel.getSliceId()
		VMxmlClass.project_name = VMmodel.getProjectName()
		VMxmlClass.slice_name = VMmodel.getSliceName()
		VMxmlClass.operating_system_type = VMmodel.getOSType()
		VMxmlClass.operating_system_version = VMmodel.getOSVersion()
		VMxmlClass.operating_system_distribution = VMmodel.getOSDistribution()
		VMxmlClass.virtualization_type = VMmodel.Server.get().getVirtTech()
		VMxmlClass.server_id = VMmodel.Server.get().getUUID()
		VMxmlClass.xen_configuration.hd_setup_type = VMmodel.getHdSetupType()
		VMxmlClass.xen_configuration.hd_origin_path = VMmodel.getHdOriginPath()
		VMxmlClass.xen_configuration.virtualization_setup_type = VMmodel.getVirtualizationSetupType()
		VMxmlClass.xen_configuration.memory_mb = VMmodel.getMemory()

		ActionController.PopulateNetworkingParams(VMxmlClass.xen_configuration.interfaces.interface, VMmodel)
