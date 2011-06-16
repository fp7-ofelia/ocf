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
		#action.virtual_machine.virtualization_type = vm.Server.get().getVirtTech()
		action.virtual_machine.xen_configuration.hd_setup_type = vm.getHdSetupType()

	@staticmethod
	def PopulateNetworkingParams(action, vm):
		print "POPULATING NETWORKKING IN VMHITHIN ACTION"
		actionIfaces = action.virtual_machine.xen_configuration.interfaces.interface
		print "actionIfaces"
		baseIface = copy.deepcopy(actionIfaces[0])
		print "baseIface"
		actionIfaces.pop()
		print "pop() empty actionIfaces"
		for index, vmIface in enumerate(vm.networkInterfaces.all()):
			currentIface = copy.deepcopy(baseIface)
			print "currentIface"+ str(vmIface.name)
			currentIface.ismgmt = vmIface.isMgmt
			print "isMgmt"+str(vmIface.isMgmt)
			currentIface.name = "eth"+str(index)
			print "name"+ "eth"+str(index)
			currentIface.mac = vmIface.mac.mac
			print "mac "+str(vmIface.mac.mac)
			#XXX: ip4s are many, but xml only accepts one
			if vmIface.ip4s.all():
				currentIface.ip = vmIface.ip4s.all()[0].ip
				print "ip "+str(vmIface.ip4s.all()[0].ip)
				currentIface.mask = vmIface.ip4s.all()[0].Ip4Range.get().netMask
				print "netmask " +str(vmIface.ip4s.all()[0].Ip4Range.get().netMask)
				currentIface.gw = vmIface.ip4s.all()[0].Ip4Range.get().gw
				print "gw"
				currentIface.dns1 = vmIface.ip4s.all()[0].Ip4Range.get().dns1
				print "dns1"
				currentIface.dns2 = vmIface.ip4s.all()[0].Ip4Range.get().dns2
				print "dns2"
			print vmIface.serverBridge.all()
			currentIface.switch_id = vmIface.serverBridge.all()[0].name
			print "switch-id"
			actionIfaces.append(currentIface)
		
						



