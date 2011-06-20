from vt_manager.communication.utils.XmlHelper import XmlHelper
from vt_manager.models.Action import Action
import logging

class MonitoringResponseDispatcher():

	'''
	Handles the Agent responses when action status changes
	'''

	@staticmethod
	def processResponse(rspec):
		from vt_manager.models.VTServer import VTServer
	
		print "-------------------> Monitoring!!!!!"
	
		for action in rspec.response.monitoring.action:
			if not action.type_ == "listActiveVMs":
				raise Exception("Cannot process Monitoring action:"+action.type_)
			try:
				actionModel = Action.getAndCheckActionByUUID(action.id)
			except Exception as e:
				logging.error("No action in DB with the incoming uuid\n%s", e)
				return

			if action.status == "ONGOING":
				print "----------------------->ONGOING"
				#ONGOING
				actionModel.setStatus(Action.ONGOING_STATUS)	
			elif action.status == "SUCCESS":
				print "----------------------->SUCCESS"
				server = VTServer.objects.get(uuid=actionModel.getObjectUUID())
				print "----------------------->SUCCESS2"
				VMMonitor.processUpdateVMsList(server,action.server.virtual_machines)	
				actionModel.destroy()

			elif action.status == "FAILED":
				print "----------------------->FAILED!!"
				actionModel.setStatus(Action.FAILED_STATUS)	
