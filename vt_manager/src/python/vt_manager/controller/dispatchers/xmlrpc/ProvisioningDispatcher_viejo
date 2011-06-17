from vt_manager.controller.drivers.VTDriver import VTDriver
from vt_manager.models.Action import Action
from vt_manager.controller.dispatchers.xmlrpc.utils.Translator import Translator
from django.db import transaction
import xmlrpclib, threading, logging, copy
from vt_manager.communication.utils.XmlHelper import XmlHelper
from vt_manager.controller.policy.PolicyManager import PolicyManager
from vt_manager.communication.XmlRpcClient import XmlRpcClient
from vt_manager.settings import ROOT_USERNAME,ROOT_PASSWORD,VTAM_URL
from vt_manager.controller.actions.ActionController import ActionController
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
				print action.virtual_machine.virtualization_type
				controller = VTDriver.getDriver(action.virtual_machine.virtualization_type)
			except Exception as e:
				logging.error(e)
				raise e
			
			#PROVISIONING CREATE
			if actionModel.getType() == Action.PROVISIONING_VM_CREATE_TYPE:
				ProvisioningDispatcher.__createVM(controller, actionModel, action)
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
			
			Server, VMmodel = controller.getServerAndCreateVM(action)
			ActionController.PopulateNetworkingParams(action, VMmodel)
			#XXX:Change action Model
			actionModel.objectUUID = VMmodel.getUUID()
			actionModel.save()

			print "[LEODEBUG] XMLRPC EOEOEOEOE"
			print Server.getAgentURL()
			print "https://"+ROOT_USERNAME+":"+ROOT_PASSWORD+"@"+VTAM_URL
			print XmlHelper.craftXmlClass(XmlHelper.getSimpleActionQuery(action))
			XmlRpcClient.callRPCMethod(Server.getAgentURL() ,"send", "https://"+ROOT_USERNAME+":"+ROOT_PASSWORD+"@"+VTAM_URL, 1, "hfw9023jf0sdjr0fgrbjk",XmlHelper.craftXmlClass(XmlHelper.getSimpleActionQuery(action)) )	
		except Exception as e:
			XmlRpcClient.callRPCMethod(threading.currentThread().callBackURL,"sendAsync",XmlHelper.getProcessingResponse(Action.FAILED_STATUS, action.id, str(e)))
			raise e 

	@staticmethod
	def __deleteStartStopRebootVM(controller, actionModel, action):

		try:

			actionModel.checkActionIsPresentAndUnique()
			print "[LEODEBUG] LLEGA "
			VMmodel =  controller.getVMbyUUID(action.virtual_machine.uuid)
			print "[LEODEBUG] VMmodel "
			print VMmodel 
			if not VMmodel:
				logging.error("VM with uuid %s not found\n" % action.virtual_machine.uuid)
				raise Exception("VM with uuid %s not found\n" % action.virtual_machine.uuid)

			elif not PolicyManager.checkPolicies(action):
				logging.error("The requested action do not pass the Aggregate Manager Policies")
				raise Exception("The requested action do not pass the Aggregate Manager Policies")
			
			#XXX:Change action Model
			actionModel.setObjectUUID(VMmodel.getUUID())
			actionModel.save()
			XmlRpcClient.callRPCMethod(VMmodel.Server.get().getAgentURL() ,"send", "https://"+ROOT_USERNAME+":"+ROOT_PASSWORD+"@"+VTAM_URL, 1, "hfw9023jf0sdjr0fgrbjk",XmlHelper.craftXmlClass(XmlHelper.getSimpleActionQuery(action)) )	
		except Exception as e:
			XmlRpcClient.callRPCMethod(threading.currentThread().callBackURL,"sendAsync",XmlHelper.getProcessingResponse(Action.FAILED_STATUS, action.id, str(e)))
			raise e 


