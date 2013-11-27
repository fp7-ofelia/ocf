import xmlrpclib, threading, copy

from utils.action import Action
from utils.xmlhelper import XmlHelper
from utils.urlutils import UrlUtils

from communication.xmlrpcclient import XmlRpcClient

from controller.actions.actioncontroller import ActionController
from controller.policies.ruletablemanager import RuleTableManager
from controller.drivers.vtdriver import VTDriver
import amsoil.core.log 

logging=amsoil.core.log.getLogger('ProvisioningDispatcher')


class ProvisioningDispatcher():
  
 
	@staticmethod
	def processProvisioning(provisioning):
		logging.debug("PROVISIONING STARTED...\n")
		for action in provisioning.action:
			actionModel = ActionController.ActionToModel(action,"provisioning")
			logging.debug("ACTION type: %s with id: %s" % (actionModel.type, actionModel.uuid))

			try:
				logging.debug("************************** 1")
				RuleTableManager.Evaluate(action,RuleTableManager.getDefaultName())
				logging.debug("************************** 2")
			except Exception as e:
				logging.debug("************************** 3" + str(e))
				a = str(e)
				if len(a)>200:
					a = a[0:199]
				
				XmlRpcClient.callRPCMethod(threading.currentThread().callBackURL,"sendAsync",XmlHelper.craftXmlClass(XmlHelper.getProcessingResponse(Action.FAILED_STATUS, action,a )))
				return None
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
				logging.debug("******************************* A")
				#PROVISIONING CREATE
				if actionModel.getType() == Action.PROVISIONING_VM_CREATE_TYPE:
					try:
						logging.debug("*********************************** B")
						vm = ProvisioningDispatcher.__createVM(controller, actionModel, action)
					except:
						vm = None
						raise
				#PROVISIONING DELETE, START, STOP, REBOOT
				else :
					logging.debug("***************************** C")
					ProvisioningDispatcher.__deleteStartStopRebootVM(controller, actionModel, action)
				logging.debug("********************************* D")
				XmlRpcClient.callRPCMethod(server.getAgentURL() ,"send", UrlUtils.getOwnCallbackURL(), 1, server.getAgentPassword(),XmlHelper.craftXmlClass(XmlHelper.getSimpleActionQuery(action)) )	
				logging.debug("********************************* E")
			except Exception as e:
				logging.debug("********************************* ERROR " + str(e) + ' ' +  str(server))
				if actionModel.getType() == Action.PROVISIONING_VM_CREATE_TYPE:
					# If the VM creation was interrupted in the network
					# configuration, the created VM won't be returned
					try:
						if not vm:
							vm = controller.getVMbyUUID(action.server.virtual_machines[0].uuid)
						controller.deleteVM(vm)
					except Exception as e:
						print "Could not delete VM. Exception: %s" % str(e)
				XmlRpcClient.callRPCMethod(threading.currentThread().callBackURL,"sendAsync",XmlHelper.craftXmlClass(XmlHelper.getProcessingResponse(Action.FAILED_STATUS, action, str(e))))

		logging.debug("PROVISIONING FINISHED...")

	@staticmethod
	def __createVM(controller, actionModel, action):
        
		try:
			logging.debug("**************************** OK - 1")
			actionModel.checkActionIsPresentAndUnique()
			logging.debug("**************************** OK - 2")
			Server, VMmodel = controller.getServerAndCreateVM(action)
			logging.debug("**************************** OK - 3")
			ActionController.PopulateNetworkingParams(action.server.virtual_machines[0].xen_configuration.interfaces.interface, VMmodel)
			logging.debug("**************************** OK - 4")
			#XXX:Change action Model
			actionModel.objectUUID = VMmodel.getUUID()
			logging.debug("**************************** OK - 5")
			return VMmodel
		except:
			raise

	@staticmethod
	def __deleteStartStopRebootVM(controller, actionModel, action):

		try:
			actionModel.checkActionIsPresentAndUnique()
			VMmodel =  controller.getVMbyUUID(action.server.virtual_machines[0].uuid)
			if not VMmodel:
				logging.error("VM with uuid %s not found\n" % action.server.virtual_machines[0].uuid)
				raise Exception("VM with uuid %s not found\n" % action.server.virtual_machines[0].uuid)
			
			#XXX:Change action Model
			actionModel.setObjectUUID(VMmodel.getUUID())
		except:
			raise 

