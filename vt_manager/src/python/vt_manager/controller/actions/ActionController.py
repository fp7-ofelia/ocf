from vt_manager.models.Action import Action
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
		tempVMclass = XmlHelper.getProcessingResponse('dummy', 'dummy', 'dummy').response.provisioning.action[0].virtual_machine
		tempVMclass.uuid = actionModel.getObjectUUID()
		action.virtual_machine = tempVMclass

	@staticmethod
	def PopulateNewActionWithVM(action, vm):
		action.id = uuid.uuid4()
		action.virtual_machine.name = vm.getName()
		action.virtual_machine.uuid = vm.getUUID()
		action.virtual_machine.project_id = vm.getProjectId()
		action.virtual_machine.slice_id = vm.getSliceId()
		action.virtual_machine.project_name = vm.getProjectName()
		action.virtual_machine.slice_name = vm.getSliceName()
		#XXX:CHECK IF IT IS NEEDED
		#action.virtual_machine.virtualization_type = vm.Server.get().getVirtTech()
		action.virtual_machine.xen_configuration.hd_setup_type = vm.getHdSetupType()

	@staticmethod
	def PopulateNetworkingParams(actionIfaces, vm):
		#actionIfaces = action.virtual_machine.xen_configuration.interfaces.interface
		baseIface = copy.deepcopy(actionIfaces[0])
		actionIfaces.pop()
		for index, vmIface in enumerate(vm.networkInterfaces.all()):
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
		actionModel.uuid = action.id
		if save is "save":
			actionModel.save()
		return actionModel						



