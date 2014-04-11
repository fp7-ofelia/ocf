import time

from vt_manager.controller.drivers.VTDriver import VTDriver
from vt_manager.models.Action import Action
from django.db import transaction
import xmlrpclib, threading, logging, copy
from vt_manager.communication.utils.XmlHelper import XmlHelper
from vt_manager.communication.XmlRpcClient import XmlRpcClient
#from vt_manager.settings.settingsLoader import ROOT_USERNAME,ROOT_PASSWORD,VTAM_IP,VTAM_PORT
from vt_manager.utils.UrlUtils import UrlUtils
from vt_manager.controller.actions.ActionController import ActionController

from vt_manager.controller.policies.RuleTableManager import RuleTableManager

#from vt_manager.communication.sfa.vm_utils.SfaCommunicator import SfaCommunicator
#from vt_manager.common.middleware.thread_local import thread_locals, pull

class ProvisioningDispatcher():
  

    @staticmethod
    def processProvisioning(provisioning):
		logging.debug("PROVISIONING STARTED...\n")
		for action in provisioning.action:
			actionModel = ActionController.ActionToModel(action,"provisioning")
			logging.debug("ACTION type: %s with id: %s" % (actionModel.type, actionModel.uuid))
			try:
				RuleTableManager.Evaluate(action,RuleTableManager.getDefaultName())
			except Exception as e:
				MAX_CHARS_ALLOWED = 200
				XmlRpcClient.callRPCMethod(threading.currentThread().callBackURL,"sendAsync",XmlHelper.craftXmlClass(XmlHelper.getProcessingResponse(Action.FAILED_STATUS, action,str(e)[0:MAX_CHARS_ALLOWED-1])))
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
				#PROVISIONING CREATE
				if actionModel.getType() == Action.PROVISIONING_VM_CREATE_TYPE:
					try:
						vm = ProvisioningDispatcher.__createVM(controller, actionModel, action)
					except:
						vm = None
						raise
				#PROVISIONING DELETE, START, STOP, REBOOT
				else :
					ProvisioningDispatcher.__deleteStartStopRebootVM(controller, actionModel, action)
				XmlRpcClient.callRPCMethod(server.getAgentURL() ,"send", UrlUtils.getOwnCallbackURL(), 1, server.getAgentPassword(),XmlHelper.craftXmlClass(XmlHelper.getSimpleActionQuery(action)) )
				return
			except Exception as e:
				if actionModel.getType() == Action.PROVISIONING_VM_CREATE_TYPE:
					# If the VM creation was interrupted in the network
					# configuration, the created VM won't be returned
					try:
						if not vm:
							vm = controller.getVMbyUUID(action.server.virtual_machines[0].uuid)
						controller.deleteVM(vm)
						# Keep actions table up-to-date after each deletion
						actionModel.delete()
					except Exception as e:
						print "Could not delete VM. Exception: %s" % str(e)
				#XmlRpcClient.callRPCMethod(threading.currentThread().callBackURL,"sendAsync",XmlHelper.craftXmlClass(XmlHelper.getProcessingResponse(Action.FAILED_STATUS, action, str(e))))
		logging.debug("PROVISIONING FINISHED...")
 

    @staticmethod
    @transaction.commit_on_success
    def __createVM(controller, actionModel, action):
        try:
            actionModel.checkActionIsPresentAndUnique()
            Server, VMmodel = controller.getServerAndCreateVM(action)
            ActionController.completeConfiguratorInActionRspec(action.server.virtual_machines[0].xen_configuration)
            ActionController.PopulateNetworkingParams(action.server.virtual_machines[0].xen_configuration.interfaces.interface, VMmodel)
	    #XXX:Change action Model
            actionModel.objectUUID = VMmodel.getUUID()
	    #actionModel.callBackUrl = threading.currentThread().callBackURL
            actionModel.save()
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
			actionModel.save()
		except:
			raise 

