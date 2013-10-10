from vt_manager.models.Action import Action
from vt_manager.models.XenVM import IMAGE_CONFIGURATORS
from vt_manager.communication.utils.XmlHelper import XmlHelper
import uuid, copy

class ActionController():
	
    @staticmethod
    def getAction(uuid):
		actions = Action.objects.filter(uuid = uuid)
		print actions
		if actions.count() ==  1:
			return actions[0]
		elif actions.count() == 0:
			raise Exception("Action with uuid %s does not exist" % uuid)
		elif actions.count() > 1:
			raise Exception("More than one Action with uuid %s" % uuid)
	
	
    @staticmethod
    def createNewAction(aType,status,objectUUID=None,description=""):
        return Action.constructor(aType,status,objectUUID,description)	

    @staticmethod
    def completeActionRspec(action, actionModel):
		action.type_ = actionModel.getType()
		#tempVMclass = XmlHelper.getProcessingResponse('dummy', None , 'dummy').response.provisioning.action[0].server.virtual_machines[0]
		#tempVMclass.uuid = actionModel.getObjectUUID()
		#action.server.virtual_machines[0] = tempVMclass

    @staticmethod
    def completeConfiguratorInActionRspec(xen_configuration):
	### TODO:CHECK How to add the configurator in the xml
		vm_path = xen_configuration.hd_origin_path
		try:
			 xen_configuration.configurator = IMAGE_CONFIGURATORS[vm_path]
		except:
	#	if vm_path == "default/default.tar.gz":
	#		xen_configuration.configurator=""
	#	elif vm_path == "spirent/spirentSTCVM.img":
	#		xen_configuration.configurator="SpirentCentOSVMConfigurator"
	#	else:
			xen_configuration.configurator=""


	#XXX: Why are these two functions here? Do not beling to the Action, aren't they?

    @staticmethod
    def PopulateNewActionWithVM(action, vm):
		action.id = uuid.uuid4()
		virtual_machine = action.server.virtual_machines[0]
		virtual_machine.name = vm.getName()
		virtual_machine.uuid = vm.getUUID()
		virtual_machine.project_id = vm.getProjectId()
		virtual_machine.slice_id = vm.getSliceId()
		virtual_machine.project_name = vm.getProjectName()
		virtual_machine.slice_name = vm.getSliceName()
		virtual_machine.xen_configuration.hd_setup_type = vm.getHdSetupType()

    @staticmethod
    def PopulateNetworkingParams(actionIfaces, vm):
		baseIface = copy.deepcopy(actionIfaces[0])
		actionIfaces.pop()
		#for index, vmIface in enumerate(vm.networkInterfaces.all().order_by('-isMgmt','id')):
		for index, vmIface in enumerate(vm.getNetworkInterfaces()):
			currentIface = copy.deepcopy(baseIface)
			currentIface.ismgmt = vmIface.isMgmt
			currentIface.name = "eth"+str(index)
			currentIface.mac = vmIface.mac.mac
			#XXX: ip4s are many, but xml only accepts one
			if vmIface.ip4s.all():
				currentIface.ip = vmIface.ip4s.all()[0].ip
				currentIface.mask = vmIface.ip4s.all()[0].Ip4Range.get().netMask
				currentIface.gw = vmIface.ip4s.all()[0].Ip4Range.get().gw
				currentIface.dns1 = vmIface.ip4s.all()[0].Ip4Range.get().dns1
				currentIface.dns2 = vmIface.ip4s.all()[0].Ip4Range.get().dns2
			currentIface.switch_id = vmIface.serverBridge.all()[0].name
			actionIfaces.append(currentIface)
		
    @staticmethod
    def ActionToModel(action, hyperaction, save = "noSave" ):
        actionModel = Action()
        actionModel.hyperaction = hyperaction
        if not action.status:
            actionModel.status = 'QUEUED'
        else:
            actionModel.status = action.status
        actionModel.type = action.type_
        print "**************************************************", action.id
        actionModel.uuid = action.id
        print "***************************************************", save
        if save is "save":
            actionModel.save()
        return actionModel						



