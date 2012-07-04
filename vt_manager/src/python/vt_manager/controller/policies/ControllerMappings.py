class ControllerMappings():
	
	@staticmethod
	def getVirtualizationTypeTag(vType):

		if vType == 'xen':
			return "['xen-configuration']"
		else:
			raise Exception("Unknown type of virtualization")
	@staticmethod
	def getVtypeValues(metaObj):
		vTypeTag = ControllerMappings.getVirtualizationTypeTag(metaObj['virtual-machine'][virtualization-type])
		
		return eval("metaObj['virtual-machine']" + vTypeTag + "['hd-setup-type']"),eval("metaObj['virtual-machine']" + vTypeTag + "['hd-origin-path']"),eval("metaObj['virtual-machine']" + vTypeTag + "['memory-mb']"),eval("metaObj['virtual-machine']" + vTypeTag + "['interfaces']['interface']['name']"),eval("metaObj['virtual-machine']" + vTypeTag + "['interfaces']['interface']['mac']"),eval("metaObj['virtual-machine']" + vTypeTag + "['interfaces']['interface']['ip']"),eval("metaObj['virtual-machine']" + vTypeTag + "['interfaces']['interface']['mask']"),eval("metaObj['virtual-machine']" + vTypeTag + "['interfaces']['interface']['gw']"),eval("metaObj['virtual-machine']" + vTypeTag + "['interfaces']['interface']['dns1']"),eval("metaObj['virtual-machine']" + vTypeTag + "['interfaces']['interface']['dns2']")

	@staticmethod
	def getNumberOfKeys(string):
		dic = eval(str)
		return len(dic.keys())
		
	

	@staticmethod
	def setConditionMappings():
		conditionMappings = {
				 	"vm.name": "metaObj['virtual-machine']['name']",
                                	"vm.uuid": "metaObj['virtual-machine']['uuid']",
                                	"vm.projectId": "metaObj['virtual-machine']['project-id']",
                                	"vm.sliceId": "metaObj['virtual-machine']['slice-id']",
                                	"vm.osType": "metaObj['virtual-machine']['operating-system-type']",
                                	"vm.osVersion": "metaObj['virtual-machine']['operating-system-version']",
                                	"vm.osDistribution": "metaObj['virtual-machine']['operating-system-distribution']",
                                	"vm.virtualizationType": "metaObj['virtual-machine']['virtualization-type']",
					"vm.hdSetupType": 'vt_manager.controller.policies.ControllerMappings.getVtypeValues(metaObj)[0]',
					"vm.hdOriginPath": 'vt_manager.controller.policies.ControllerMappings.getVtypeValues(metaObj)[1]',
					"vm.memory": 'vt_manager.controller.policies.ControllerMappings.getVtypeValues(metaObj)[2]',
					"vm.interfaceName": 'vt_manager.controller.policies.ControllerMappings.getVtypeValues(metaObj)[3]',
					"vm.interfaceMac": 'vt_manager.controller.policies.ControllerMappings.getVtypeValues(metaObj)[4]',
					"vm.interfaceIp": 'vt_manager.controller.policies.ControllerMappings.getVtypeValues(metaObj)[5]',
					"vm.interfaceMask": 'vt_manager.controller.policies.ControllerMappings.getVtypeValues(metaObj)[6]',
					"vm.interfaceGw": 'vt_manager.controller.policies.ControllerMappings.getVtypeValues(metaObj)[7]',
					"vm.interfaceDns1":'vt_manager.controller.policies.ControllerMappings.getVtypeValues(metaObj)[8]',
					"vm.interfaceDns1":'vt_manager.controller.policies.ControllerMappings.getVtypeValues(metaObj)[9]',
					"vm.Ninterfaces": 'vt_manager.controller.policies.ControllerMappings.getNumberOfKeys(\'eval(len("metaObj[\'virtual-machine\']" + vTypeTag + "[\'interfaces\'].keys()"))\')',
					#TODO: A function to count the number of vm's
				#	"vm.Nvms": 'len("metaObj[\'actions\'][0]")',
                                	"action.type":"metaObj['actions'][0]"}

		return conditionMappings
		


	@staticmethod
	def getConditionMappings():
		return ControllerMappings.setConditionMappings()
