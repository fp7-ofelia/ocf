from vt_manager.communication.utils.XmlHelper import XmlHelper
from vt_manager.models.Action import Action
import logging

class MonitoringResponseDispatcher():

	'''
	Handles the Agent responses when action status changes
	'''

	@staticmethod
	def processResponse(rspec):
	
		print "-------------------> Monitoring!!!!!"
	
		for action in rspec.response.monitoring.action:
			print action
			if not action.type_ == "listActiveVMs":
				raise Exception("Cannot process Monitoring action:"+action.type_)
			try:
				if action.id == "callback":
					print '---------------------->Libvirt Monitoring!!!'
					from vt_manager.controller.monitoring.VMMonitor import VMMonitor
					from vt_manager.models.VTServer import VTServer
                                        print '------>UUID',action.server.virtual_machines[0].uuid
					print '------>STATUS',action.server.virtual_machines[0].status
					VMMonitor.processUpdateVMsListFromCallback(action.server.virtual_machines[0].uuid,action.server.virtual_machines[0].status,rspec)
					print '---------------------->LibvirtMonitoring Finished!!!'
					return
				else:
					actionModel = Action.getAndCheckActionByUUID(action.id)
			except Exception as e:
				logging.error("No action in DB with the incoming uuid\n%s", e)
				return

			if action.status == "ONGOING":
				print "----------------------->ONGOING"
				#ONGOING
				actionModel.setStatus(Action.ONGOING_STATUS)
				return
			elif action.status == "SUCCESS":
				from vt_manager.models.VTServer import VTServer
				from vt_manager.controller.monitoring.VMMonitor import VMMonitor

				print "----------------------->SUCCESS"
				server = VTServer.objects.get(uuid=actionModel.getObjectUUID())
				print "----------------------->SUCCESS2"
				VMMonitor.processUpdateVMsList(server,action.server.virtual_machines)	
				actionModel.destroy()
			elif action.status == "FAILED":
				print "----------------------->FAILED!!"
				actionModel.setStatus(Action.FAILED_STATUS)	
