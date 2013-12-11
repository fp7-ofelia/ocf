from utils.xmlhelper import XmlHelper
from utils.action import Action

import logging

class MonitoringResponseDispatcher():
	'''
	Handles the Agent responses when action status changes
	'''

	@staticmethod
	def processResponse(rspec):
		logging.debug("-------------------> Monitoring!!!!!")
		for action in rspec.response.monitoring.action:
			logging.debug(action)
			if not action.type_ == "listActiveVMs":
				raise Exception("Cannot process Monitoring action:"+action.type_)
			try:
				if action.id == "callback":
					logging.debug('---------------------->Libvirt Monitoring!!!')
					from controller.monitoring.vmmonitor import VMMonitor
					from resources.vtserver import VTServer
                                        print '------>UUID',action.server.virtual_machines[0].uuid
					logging.debug('------>STATUS',action.server.virtual_machines[0].status)
					VMMonitor.processUpdateVMsListFromCallback(action.server.virtual_machines[0].uuid,action.server.virtual_machines[0].status,rspec)
					logging.debug('---------------------->LibvirtMonitoring Finished!!!')
					return
				else:
					actionModel = Action.getAndCheckActionByUUID(action.id)
			except Exception as e:
				logging.error("No action in DB with the incoming uuid\n%s", e)
				return

			if action.status == "ONGOING":
				logging.debug("----------------------->ONGOING")
				#ONGOING
				actionModel.setStatus(Action.ONGOING_STATUS)
				return
			elif action.status == "SUCCESS":
				from vt_manager.models.VTServer import VTServer
				from vt_manager.controller.monitoring.VMMonitor import VMMonitor

				logging.debug("----------------------->SUCCESS")
				server = VTServer.objects.get(uuid=actionModel.getObjectUUID())
				logging.debug("----------------------->SUCCESS2")
				VMMonitor.processUpdateVMsList(server,action.server.virtual_machines)	
				actionModel.destroy()
			elif action.status == "FAILED":
				logging.debug("----------------------->FAILED!!")
				actionModel.setStatus(Action.FAILED_STATUS)	
