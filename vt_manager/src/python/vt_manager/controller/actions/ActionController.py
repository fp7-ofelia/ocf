from vt_manager.models.Action import Action
from vt_manager.communication.utils.XmlHelper import XmlHelper
import uuid

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
	def PopulateNewAction(action, vm):
		action.id = uuid.uuid4()
		action.virtual_machine.name = vm.getName()
		action.virtual_machine.uuid = vm.getUUID()
		action.virtual_machine.project_id = vm.getProjectId()
		action.virtual_machine.slice_id = vm.getSliceId()
		action.virtual_machine.project_name = vm.getProjectName()
		action.virtual_machine.slice_name = vm.getSliceName()
		#action.virtual_machine.virtualization_type = vm.Server.get().getVirtTech()
		action.virtual_machine.xen_configuration.hd_setup_type = vm.getHdSetupType()
