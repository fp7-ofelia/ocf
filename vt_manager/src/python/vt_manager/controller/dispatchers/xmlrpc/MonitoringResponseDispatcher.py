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

			try:
				actionModel = Action.getAndCheckActionByUUID(action.id)
			except Exception as e:
				logging.error("No action in DB with the incoming uuid\n%s", e)
				return

			'''
			If the response is for an action only in QUEUED or ONGOING status, SUCCESS or FAILED actions are finished
			'''
				#TODO
