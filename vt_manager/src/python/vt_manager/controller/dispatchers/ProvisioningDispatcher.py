from vt_manager.controller.dispatchers.Dispatcher import Dispatcher
from vt_manager.controller.drivers.VTDriver import VTDriver
from vt_manager.models.Action import Action
from vt_manager.controller.utils.Translator import Translator
from django.db import transaction
import xmlrpclib, threading, logging, copy
from vt_manager.communication.utils.XmlUtils import XmlHelper

class ProvisioningDispatcher(Dispatcher):
  
	def __init__(self):
		self.Dispatcher.__init__(self)
 
	@staticmethod
	def __createVM(controller, actionModel, action):
        
		try:
			actionModel.checkActionIsPresentAndUnique()

			if not PolicyManager.checkPolicies(action):
				logging.error("The requested action do not pass the Aggregate Manager Policies")
				raise Exception("The requested action do not pass the Aggregate Manager Policies")
			
			Server, VMmodel = controller.getServerAndCreateVM(action)
        
			#XXX:Change action Model
			actionModel.vmUUID = VMmodel.getUUID()
			actionModel.save()

			ProvisioningDispatcher.prefijo__connectAndSendAgent(Server, action)
			print "[LEODEBUG] Despues del sendAgent"
		except Exception as e:
			print "[LEODEBUG] en la excepcion"
			ProvisioningDispatcher.prefijo__connectAndSendPlugin(threading.currentThread().callBackURL, XmlHelper.getProcessingResponse(Action.ACTION_STATUS_FAILED_TYPE, action.id, str(e)))
			raise e 

	@staticmethod
	def __deleteStartStopRebootVM(controller, actionModel, action):

		try:

			actionModel.checkActionIsPresentAndUnique()

			VMmodel =  controller.getVMbyUUID(action.virtual_machine.uuid)

			if not VMmodel:
				logging.error("VM with uuid %s not found\n" % action.virtual_machine.uuid)
				raise Exception("VM with uuid %s not found\n" % action.virtual_machine.uuid)

			elif not PolicyManager.checkPolicies(action):
				logging.error("The requested action do not pass the Aggregate Manager Policies")
				raise Exception("The requested action do not pass the Aggregate Manager Policies")
			
			#XXX:Change action Model
			actionModel.setVMuuid(VMmodel.getUUID())
			actionModel.save()
			ProvisioningDispatcher.prefijo__connectAndSendAgent(VMmodel.getServer().getAgentURL(), action)
		except Exception as e:
			ProvisioningDispatcher.prefijo__connectAndSendPlugin(threading.currentThread().callBackURL, XmlHelper.getProcessingResponse(Action.ACTION_STATUS_FAILED_TYPE, action.id, str(e)))
			raise e

 
	@staticmethod
	@transaction.commit_on_success
	def processProvisioning(provisioning):

		logging.debug("PROVISIONING STARTED...\n")
		for action in provisioning.action:
			actionModel = Translator.ActionToModel(action,"provisioning")
			logging.debug("ACTION type: %s with id: %s" % (actionModel.type, actionModel.uuid))
			
			try:
				print "[LEODEBUG] aca llega"
				controller = VTDriver.getDriver(action.virtual_machine.virtualization_type)
			except Exception as e:
				logging.error(e)
			
			#PROVISIONING CREATE

			if actionModel.getType() == Action.ACTION_TYPE_CREATE_TYPE:
            	
				ProvisioningDispatcher.__createVM(controller, actionModel, action)

			#PROVISIONING DELETE, START, STOP, REBOOT
 
			else :

				ProvisioningDispatcher.__deleteStartStopRebootVM(controller, actionModel, action)

		logging.debug("PROVISIONING FINISHED...")
