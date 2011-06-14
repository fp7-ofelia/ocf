from vt_manager.controller.drivers.VTDriver import VTDriver
from vt_manager.models.Action import Action
from vt_manager.controller.dispatchers.xmlrpc.utils.Translator import Translator
from django.db import transaction
import xmlrpclib, threading, logging, copy
from vt_manager.communication.utils.XmlHelper import XmlHelper
from vt_manager.controller.policy.PolicyManager import PolicyManager
from vt_manager.communication.XmlRpcClient import XmlRpcClient
from vt_manager.settings import ROOT_USERNAME,ROOT_PASSWORD,VTAM_URL
class ProvisioningDispatcher():
  
	def __init__(self):
		self.Dispatcher.__init__(self)
 
	@staticmethod
	@transaction.commit_on_success
	def processProvisioning(provisioning):

		logging.debug("PROVISIONING STARTED...\n")
		for action in provisioning.action:
			actionModel = Translator.ActionToModel(action,"provisioning")
			logging.debug("ACTION type: %s with id: %s" % (actionModel.type, actionModel.uuid))
			
			try:
				print "[LEODEBUG] aca llega"
				print action.virtual_machine.virtualization_type
				controller = VTDriver.getDriver(action.virtual_machine.virtualization_type)
			except Exception as e:
				print "[LEODEBUG] NO CONTROLLER"
				logging.error(e)
				raise e
			
			#PROVISIONING CREATE
			print "[LEODEBUG] action.getType()"
			if actionModel.getType() == Action.ACTION_TYPE_CREATE_TYPE:
				print "[LEODEBUG] createVM"
				ProvisioningDispatcher.__createVM(controller, actionModel, action)
				print "[LEODEBUG] post createVM"
			#PROVISIONING DELETE, START, STOP, REBOOT
 
			else :

				ProvisioningDispatcher.__deleteStartStopRebootVM(controller, actionModel, action)

		logging.debug("PROVISIONING FINISHED...")


	@staticmethod
	def __createVM(controller, actionModel, action):
        
		try:
			actionModel.checkActionIsPresentAndUnique()

			if not PolicyManager.checkPolicies(action):
				logging.error("The requested action do not pass the Aggregate Manager Policies")
				raise Exception("The requested action do not pass the Aggregate Manager Policies")
			
			print "[LEODEBUG] step1"	
			Server, VMmodel = controller.getServerAndCreateVM(action)
			print "[LEODEBUG] step2"
			#XXX:Change action Model
			actionModel.vmUUID = VMmodel.getUUID()
			print "[LEODEBUG] step3"
			actionModel.save()
			print "[LEODEBUG] step4"

			XmlRpcClient.callRPCMethod(Server.getAgentURL() ,"send", "https://"+ROOT_USERNAME+":"+ROOT_PASSWORD+"@"+VTAM_URL, 1, "hfw9023jf0sdjr0fgrbjk",XmlHelper.craftXmlClass(XmlHelper.getSimpleActionQuery(action)) )	
			print "[LEODEBUG] Despues del sendAgent"
		except Exception as e:
			print "[LEODEBUG] en la excepcion"
			#XmlRpcClient.callRPCMethod(threading.currentThread().callBackURL,"sendAsync",XmlHelper.getProcessingResponse(Action.ACTION_STATUS_FAILED_TYPE, action.id, str(e)))
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

