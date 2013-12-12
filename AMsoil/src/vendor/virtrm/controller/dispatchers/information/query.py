from controller.actions.action import ActionController
from controller.drivers.virt import VTDriver
from resources.resourceshash import ResourcesHash
from utils.xmlhelper import XmlHelper
import xmlrpclib, threading, logging, copy

class InformationDispatcher():

	@staticmethod
	def listResources(remoteHashValue, projectUUID = 'None', sliceUUID ='None'):
		logging.debug("Enter listResources")
		info_rspec = XmlHelper.getSimpleInformation()
		servers = VTDriver.getAllServers()
		base_vm = copy.deepcopy(info_rspec.response.information.resources.server[0].virtual_machine[0])
		if not servers:
			logging.debug("No VTServers available")
			info_rspec.response.information.resources.server.pop()
			resources_string = XmlHelper.craftXmlClass(info_rspec)
			local_hash_value = str(hash(resources_string))
		else:
			for s_index, server in enumerate(servers):
				if(s_index == 0):
					baseServer = copy.deepcopy(info_rspec.response.information.resources.server[0])
				if(s_index != 0):
					new_server = copy.deepcopy(baseServer)
					info_rspec.response.information.resources.server.append(new_server)
				InformationDispatcher.__ServerModelToClass(server, info_rspec.response.information.resources.server[s_index] )
				if (projectUUID is not 'None'):
					vms = server.getVMs(projectId = projectUUID)
				else:
					vms = server.getVMs()
				if not vms:
					logging.debug("No VMs available")
					if info_rspec.response.information.resources.server[s_index].virtual_machine:
						info_rspec.response.information.resources.server[s_index].virtual_machine.pop()
				elif (sliceUUID is not 'None'):
					vms = vms.filter(sliceId = sliceUUID)
					if not vms:
						logging.error("No VMs available")
						info_rspec.response.information.resources.server[s_index].virtual_machine.pop()
				for vIndex, vm in enumerate(vms):
					if (vIndex != 0):
						newVM = copy.deepcopy(base_vm)
						info_rspec.response.information.resources.server[s_index].virtual_machine.append(newVM)
					InformationDispatcher.__VMmodelToClass(vm, info_rspec.response.information.resources.server[s_index].virtual_machine[vIndex])
			resources_string = XmlHelper.craftXmlClass(info_rspec)
			local_hash_value = str(hash(resources_string))
		try:
			r_hash_object = resourcesHash.objects.get(projectUUID = projectUUID, sliceUUID = sliceUUID)
			r_hash_object.hashValue = local_hash_value
			r_hash_object.save()
		except:
			r_hash_object = resourcesHash(hashValue = local_hash_value, projectUUID= projectUUID, sliceUUID = sliceUUID)
			r_hash_object.save()
		if remoteHashValue == r_hash_object.hashValue:
			return local_hash_value, ''
		else:
			return local_hash_value, resources_string
	
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
