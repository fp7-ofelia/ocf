from vt_manager.controller.policies.utils.PolicyLogger import PolicyLogger

class ControllerMappings():
	
	logger = PolicyLogger.getLogger()
	
	@staticmethod
	def getActionMappings():
		actionMappings = { "None":"None",
				   "LogVM": ControllerMappings.logVM,}
		return actionMappings				     

	@staticmethod
	def getConditionMappings():
		conditionMappings = {
					#SERVER mappings
					"server.name":"metaObj.server.get_name()",
					"server.uuid":"metaObj.server.get_uuid()",
					"server.virtualization_type":"metaObj.server.get_virtualization_type()",
					"server.status":"metaObj.server.get_status()",
				
					#Project mappings
					"project.number_of_vms":ControllerMappings.getNumberOfVMs,	
					"project.name":"metaObj.server.virtual_machines[0].get_project_name()",
					"project.uuid":"metaObj.server.virtual_machines[0].get_project_uuid()",
				
					#Slice mappings
					"slice.name": "metaObj.server.virtual_machines[0].get_slice_name()",
					"slice.uuid":"metaObj.server.virtual_machines[0].get_slice_uuid()",
	
					#VM mappings
				 	"vm.name": "metaObj.server.virtual_machines[0].get_name()",
                                	"vm.uuid": "metaObj.server.virtual_machines[0].get_uuid()",
					"vm.status":"metaObj.server.virtual_machines[0].get_status()",
					"vm.hd_origin_path":"metaObj.server.virtual_machines[0].get_hd_origin_path()",
					"vm.operating_system_type":"metaObj.server.virtual_machines[0].get_operating_system_type()",
					"vm.operating_system_version":"metaObj.server.virtual_machines[0].get_operating_system_version()",
					"vm.operating_system_distribution":"metaObj.server.virtual_machines[0].get_operating_system_distribution()",
					"vm.virtualization_type":"metaObj.server.virtual_machines[0].get_virtualization_type()",
					"vm.hd_size_mb":ControllerMappings.getVMHDMemory,
					"vm.memory_mb": ControllerMappings.getVMMemory, 
					
					}
		returnMapps = dict()
		List = sorted(conditionMappings.iterkeys())
		for key in List:
			returnMapps[key] = conditionMappings[key]
		return returnMapps

	@staticmethod
	def getValueFromConfiguration(metaObj,metaObjGetter):
		metaObjPath = "metaObj.server.virtual_machines[0]"
		metaObjConf = eval('metaObj.server.virtual_machines[0].get_virtualization_type()')

		conf = '.' + str(metaObjConf).lower() + '_configuration.'
		value = metaObjPath + conf + metaObjGetter
		return eval(value)

	@staticmethod
	def getVMMemory(metaObj):
		return ControllerMappings.getValueFromConfiguration(metaObj,'get_memory_mb()')
	
	@staticmethod
	def getVMHDMemory(metaObj):
		return ControllerMappings.getValueFromConfiguration(metaObj,'get_hd_size_mb()')

	@staticmethod
	def getNumberOfVMs(metaObj):
		from vt_manager.models import VirtualMachine

		projectUUID = str(metaObj.server.virtual_machines[0].get_project_id())
		return len(VirtualMachine.objects.filter(projectId = projectUUID))

	@staticmethod
	def logVM(metaObj):
		ControllerMappings.logger.debug("[NAME:%s|RAM:%s|HD:%s]" %(eval("metaObj.server.virtual_machines[0].get_name()"),ControllerMappings.getVMMemory(metaObj),ControllerMappings.getVMHDMemory(metaObj)))
