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

class ProvisioningDispatcher():
  
 
	@staticmethod
	def processProvisioning(provisioning):
		logging.debug("PROVISIONING STARTED...\n")
		for action in provisioning.action:
			actionModel = ActionController.ActionToModel(action,"provisioning")
			logging.debug("ACTION type: %s with id: %s" % (actionModel.type, actionModel.uuid))

			try:
				print '--------------ProvisioningDispatcher---------------EvaluateProcess'
				RuleTableManager.Evaluate(action,RuleTableManager.getDefaultName())
			except Exception as e:
				a = str(e)
				if len(a)>200:
					a = a[0:199]
				print '---------------ProvisioningDispatcher-----------------------Exception-Evaluating'
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
				print '--------------ProvisioningDispatcher---------------controller,server get',controller,server
			except Exception as e:
				print '--------------ProvisioningDispatcher---------------controller,server get--Exception'
				logging.error(e)
				raise e
		
			try:	
				#PROVISIONING CREATE
				print '--------------ProvisioningDispatcher---------------Before Create'
				if actionModel.getType() == Action.PROVISIONING_VM_CREATE_TYPE:
					try:
						print '--------------ProvisioningDispatcher---------------Lets create it'
						vm = ProvisioningDispatcher.__createVM(controller, actionModel, action)
						print 'VM Created OK'
					except:
						print '--------------ProvisioningDispatcher---------------creation was wrong'
						vm = None
						raise
				#PROVISIONING DELETE, START, STOP, REBOOT
				else :
					print '--------------ProvisioningDispatcher---------------CRUD VM?'
					ProvisioningDispatcher.__deleteStartStopRebootVM(controller, actionModel, action)

				print '--------------ProvisioningDispatcher---------------BeforSend'
				XmlRpcClient.callRPCMethod(server.getAgentURL() ,"send", UrlUtils.getOwnCallbackURL(), 1, server.getAgentPassword(),XmlHelper.craftXmlClass(XmlHelper.getSimpleActionQuery(action)) )	
				print 'sent OK'
			except Exception as e:
				print 'ALL_WROOOOONG--------------ProvisioningDispatcher---------------all wrong'
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
	@transaction.commit_on_success
	def __createVM(controller, actionModel, action):
        
		try:
			print '--------------ProvisioningDispatcher---------------CREATE VM Function'
			actionModel.checkActionIsPresentAndUnique()
			print '--------------ActionModel OK'
			Server, VMmodel = controller.getServerAndCreateVM(action)
			print '--------------GetServerAndCreateVM---OK'
			print 'HERE-------------------------------------------',VMmodel.name
			ActionController.PopulateNetworkingParams(action.server.virtual_machines[0].xen_configuration.interfaces.interface, VMmodel)
			print 'PopulateNetworkParams OK'
			#XXX:Change action Model
			actionModel.objectUUID = VMmodel.getUUID()
			print 'UUID chenged'			
			actionModel.save()
			print 'saved'
			return VMmodel
		except:
			print '--------------ProvisioningDispatcher---------------CREATE VM FAILED'
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

