from communications.XmlRpcClient import XmlRpcClient
from utils.Logger import Logger
"""
	@author: msune
	
	Monitoring dispatcher. Selects appropriate Driver for VT technology
"""

class MonitoringDispatcher: 
	
	logger = Logger.getLogger()	
	
	@staticmethod
	def __get_dispatcher(vtype):

		#Import of Dispatchers must go here to avoid import circular dependency 		
		from xen.monitoring.XenMonitoringDispatcher import XenMonitoringDispatcher

		if vtype == "xen": 
			return XenMonitoringDispatcher 
		else:
			raise Exception("Virtualization type not supported by the agent")	
	
	@staticmethod
	def __dispatch_action(dispatcher,action,server):
		#Gathering information
		if action.type_ == "listActiveVMs":
			return dispatcher.list_active_vms(action.id,server)
		raise Exception("Unknown action type")
	
	@staticmethod
	def process(monitoring):
		for action in monitoring.action:
			server = action.server
			try:
				dispatcher = MonitoringDispatcher.__get_dispatcher(server.virtualization_type)	
			except Exception as e:
				XmlRpcClient.sendAsyncMonitoringActionStatus(action.id,"FAILED",str(e))
				MonitoringDispatcher.logger.error(str(e))	
				return
			try:
				# Send async notification
				XmlRpcClient.sendAsyncMonitoringActionStatus(action.id,"ONGOING","")
				MonitoringDispatcher.logger.debug("After sending ongoing")	
				MonitoringDispatcher.__dispatch_action(dispatcher,action,server)	
			except Exception as e:
				MonitoringDispatcher.logger.error(str(e))	
				raise e
	
	##Abstract methods definition for MonitoringDispatchers
	#Inventory
	@staticmethod
	def list_active_vms(id,server):
		raise Exception("Abstract method cannot be called")	
