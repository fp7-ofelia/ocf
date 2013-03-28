'''
	@author: msune
	@author: lbergesio

	Monitoring dispatcher. Selects appropiate Driver for VT tech or for server system in general
'''

from communications.XmlRpcClient import XmlRpcClient
from utils.Logger import Logger
from monitoring.ServerMonitoring import ServerMonitoring

class MonitoringDispatcher: 
	
	logger = Logger.getLogger()	

	@staticmethod
	def __getMonitoringDispatcher(vtype):

		#Import of Dispatchers must go here to avoid import circular dependecy 		
		from xen.monitoring.XenMonitoringDispatcher import XenMonitoringDispatcher

		if vtype == "xen": 
			return XenMonitoringDispatcher 
		else:
			raise Exception("Virtualization type not supported by the agent")	
	
	@staticmethod
	def __dispatchAction(dispatcher,action,server):
		#Gathering information
		if action.type_ == "listActiveVMs":
			return dispatcher.listActiveVMs(action.id,server)
		elif action.type_ == "statistics":
			MonitoringDispatcher.logger.error("LEODEBUG TENGO EL DISPATCHER DE XEN Y STATICS")
			return dispatcher.serverStatistics(action.id, server)
		raise Exception("Unknown action type")


	@staticmethod
	def processMonitoring(monitoring):

		MonitoringDispatcher.logger.error("iNTRO EN EL PROCESSMONITORING")	
		for action in monitoring.action:
			server = action.server
			try:
				dispatcher = MonitoringDispatcher.__getMonitoringDispatcher(server.virtualization_type)	
			except Exception as e:
				XmlRpcClient.sendAsyncMonitoringActionStatus(action.id,"FAILED",str(e))
				MonitoringDispatcher.logger.error("LEODEBUG PETA EN EL PROCESSMONITORING")	
				MonitoringDispatcher.logger.error(str(e))	
				return

			try:
				#Send async notification
				XmlRpcClient.sendAsyncMonitoringActionStatus(action.id,"ONGOING","")
				MonitoringDispatcher.logger.debug("After sending ongoing")	
				MonitoringDispatcher.__dispatchAction(dispatcher,action,server)	
			except Exception as e:
				MonitoringDispatcher.logger.error(str(e))	
				raise e


	##Abstract methods definition for MonitoringDispatchers
	#Inventory
	@staticmethod
	def listActiveVMs(id,server):
		raise Exception("Abstract method cannot be called")	

	@staticmethod
	def serverStatistics(action_id, server):
		try:
			server = ServerMonitoring.getTopStatistics(server)
			server = ServerMonitoring.getDfStatistics(server)
                        XmlRpcClient.sendAsyncStatisticsMonitoring(action_id,"SUCCESS",server)
		except Exception as e:
			MonitoringDispatcher.logger.error(str(e))
                        XmlRpcClient.sendAsyncMonitoringActionStatus(action_id,"FAILED",str(e))
			return
		

