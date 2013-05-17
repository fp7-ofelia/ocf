from vt_manager.communication.utils.XmlHelper import XmlHelper
from vt_manager.models.Action import Action
import logging
from vt_manager.controller.monitoring.StatisticsMonitor import StatisticsMonitor

class MonitoringResponseDispatcher():

	'''
	Handles the Agent responses when action status changes
	'''

	@staticmethod
	def processResponse(rspec):
	
		for action in rspec.response.monitoring.action:
			print action
			if action.type_ == "listActiveVMs":
				try:
					if action.id == "callback":
						from vt_manager.controller.monitoring.VMMonitor import VMMonitor
						from vt_manager.models.VTServer import VTServer
						VMMonitor.processUpdateVMsListFromCallback(action.server.virtual_machines[0].uuid,action.server.virtual_machines[0].status,rspec)
						return
					else:
						actionModel = Action.getAndCheckActionByUUID(action.id)
				except Exception as e:
					logging.error("No action in DB with the incoming uuid\n%s", e)
					return

				if action.status == "ONGOING":
					#ONGOING
					actionModel.setStatus(Action.ONGOING_STATUS)
					return
				elif action.status == "SUCCESS":
					from vt_manager.models.VTServer import VTServer
					from vt_manager.controller.monitoring.VMMonitor import VMMonitor
	
					server = VTServer.objects.get(uuid=actionModel.getObjectUUID())
					VMMonitor.processUpdateVMsList(server,action.server.virtual_machines)	
					actionModel.destroy()
				elif action.status == "FAILED":
					actionModel.setStatus(Action.FAILED_STATUS)	
			elif action.type_ == "statistics":
				if action.status == "ONGOING":
					#ONGOING
					logging.debug("LEODEBUG LLEGO UN ONGOING\n\n\n\n\n")
					actionModel.setStatus(Action.ONGOING_STATUS)
					return
				elif action.status == "SUCCESS":
					logging.debug("LEODEBUG ACTION QUE LLEGA")
					logging.error(XmlHelper.craftXmlClass(rspec))	
					logging.debug(action.server)
					StatisticsMonitor.storeStatistics(action.server)
					actionModel.destroy()
                                elif action.status == "FAILED":
                                        actionModel.setStatus(Action.FAILED_STATUS)
			
			else:
				raise Exception("Cannot process Monitoring action:"+action.type_)
