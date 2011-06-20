from vt_manager.communication.utils.XmlHelper import XmlHelper
from vt_manager.models.Action import Action
from vt_manager.models.VirtualMachine import VirtualMachine
import logging

class ProvisioningResponseDispatcher():

	'''
	Handles the Agent responses when action status changes
	'''

	@staticmethod
	def processResponse(rspec):
		for action in rspec.response.monitoring.action:
			if not action.type == "listActiveVMs":
				raise Exception("Cannot process Monitoring action:"+action.type)
			try:
				actionModel = Action.getAndCheckActionByUUID(action.id)
			except Exception as e:
				logging.error("No action in DB with the incoming uuid\n%s", e)
				return

			if action.status == "ONGOING":
				#ONGOING
				actionModel.setStatus(Action.ONGOING_STATUS)	
			elif action.status == "SUCCESS":
				server = VTServer.objects.get(uuid=actionModel.getObjectUUID())
				VMMonitor.processUpdateVMsList(server,action.server.virtual_machines)	
				actionModel.destroy()

			elif action.status == "FAILED":
				actionModel.setStatus(Action.FAILED_STATUS)	
