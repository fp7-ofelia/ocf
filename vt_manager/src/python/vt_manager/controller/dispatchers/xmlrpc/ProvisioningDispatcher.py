from vt_manager.controller.drivers.VTDriver import VTDriver
from vt_manager.models.Action import Action
from django.db import transaction
import xmlrpclib, threading, logging, copy
from vt_manager.communication.utils.XmlHelper import XmlHelper
from vt_manager.controller.policy.PolicyManager import PolicyManager
from vt_manager.communication.XmlRpcClient import XmlRpcClient
#from vt_manager.settings.settingsLoader import ROOT_USERNAME,ROOT_PASSWORD,VTAM_IP,VTAM_PORT
from vt_manager.utils.UrlUtils import UrlUtils
from vt_manager.controller.actions.ActionController import ActionController

class ProvisioningDispatcher():
  
 
	@staticmethod
	def processProvisioning(provisioning):

		logging.debug("PROVISIONING STARTED...\n")
		for action in provisioning.action:
			actionModel = ActionController.ActionToModel(action,"provisioning")
			logging.debug("ACTION type: %s with id: %s" % (actionModel.type, actionModel.uuid))
			
			try:
				controller = VTDriver.getDriver(action.server.virtualization_type)

				#XXX:Change this when xml schema is updated
				server = VTDriver.getServerByUUID(action.server.uuid)
				#if actionModel.getType() == Action.PROVISIONING_VM_CREATE_TYPE:
				#	server = VTDriver.getServerByUUID(action.virtual_machine.server_id)
				#else:
				#	server = VTDriver.getVMbyUUID(action.virtual_machine.uuid).Server.get()
			except Exception as e:
				logging.error(e)
				raise e
		
			try:	
				#PROVISIONING CREATE
				if actionModel.getType() == Action.PROVISIONING_VM_CREATE_TYPE:
					vm = ProvisioningDispatcher.__createVM(controller, actionModel, action)
				#PROVISIONING DELETE, START, STOP, REBOOT
	 
				else :
	
					ProvisioningDispatcher.__deleteStartStopRebootVM(controller, actionModel, action)

				XmlRpcClient.callRPCMethod(server.getAgentURL() ,"send", UrlUtils.getOwnCallbackURL(), 1, server.getAgentPassword(),XmlHelper.craftXmlClass(XmlHelper.getSimpleActionQuery(action)) )	
			except Exception as e:
				if actionModel.getType() == Action.PROVISIONING_VM_CREATE_TYPE:
					controller.deleteVM(vm)
				XmlRpcClient.callRPCMethod(threading.currentThread().callBackURL,"sendAsync",XmlHelper.craftXmlClass(XmlHelper.getProcessingResponse(Action.FAILED_STATUS, action, str(e))))

		

		logging.debug("PROVISIONING FINISHED...")

	@staticmethod
	@transaction.commit_on_success
	def __createVM(controller, actionModel, action):
        
		try:
			actionModel.checkActionIsPresentAndUnique()

			if not PolicyManager.checkPolicies(action):
				logging.error("The requested action do not pass the Aggregate Manager Policies")
				raise Exception("The requested action do not pass the Aggregate Manager Policies")
			
			Server, VMmodel = controller.getServerAndCreateVM(action)
			ActionController.PopulateNetworkingParams(action.server.virtual_machines[0].xen_configuration.interfaces.interface, VMmodel)
			#XXX:Change action Model
			actionModel.objectUUID = VMmodel.getUUID()
			actionModel.save()
			return VMmodel
		except:
			raise
#			XmlRpcClient.callRPCMethod(Server.getAgentURL() ,"send", "https://"+ROOT_USERNAME+":"+ROOT_PASSWORD+"@"+VTAM_IP+":"+VTAM_PORT, 1, "hfw9023jf0sdjr0fgrbjk",XmlHelper.craftXmlClass(XmlHelper.getSimpleActionQuery(action)) )	
#		except Exception as e:
#			XmlRpcClient.callRPCMethod(threading.currentThread().callBackURL,"sendAsync",XmlHelper.getProcessingResponse(Action.FAILED_STATUS, action.id, str(e)))
#			controller.deleteVM(VMmodel)
#			raise e 

	@staticmethod
	def __deleteStartStopRebootVM(controller, actionModel, action):

		try:

			actionModel.checkActionIsPresentAndUnique()
			VMmodel =  controller.getVMbyUUID(action.server.virtual_machines[0].uuid)
			if not VMmodel:
				logging.error("VM with uuid %s not found\n" % action.server.virtual_machines[0].uuid)
				raise Exception("VM with uuid %s not found\n" % action.server.virtual_machines[0].uuid)

			elif not PolicyManager.checkPolicies(action):
				logging.error("The requested action do not pass the Aggregate Manager Policies")
				raise Exception("The requested action do not pass the Aggregate Manager Policies")
			
			#XXX:Change action Model
			actionModel.setObjectUUID(VMmodel.getUUID())
			actionModel.save()
		except:
			raise 
#			XmlRpcClient.callRPCMethod(VMmodel.Server.get().getAgentURL() ,"send", "https://"+ROOT_USERNAME+":"+ROOT_PASSWORD+"@"+VTAM_IP+":"+VTAM_PORT, 1, "hfw9023jf0sdjr0fgrbjk",XmlHelper.craftXmlClass(XmlHelper.getSimpleActionQuery(action)) )	
#		except Exception as e:
#			XmlRpcClient.callRPCMethod(threading.currentThread().callBackURL,"sendAsync",XmlHelper.getProcessingResponse(Action.FAILED_STATUS, action.id, str(e)))
#			raise e 


