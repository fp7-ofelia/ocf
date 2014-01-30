'''
	@author: msune
	
	Monitoring dispatcher. Selects appropiate Driver for VT tech
'''

from communications.XmlRpcClient import XmlRpcClient
from utils.Logger import Logger

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

		raise Exception("Unknown action type")


	@staticmethod
	def processMonitoring(monitoring):

		for action in monitoring.action:
			server = action.server
			try:
				dispatcher = MonitoringDispatcher.__getMonitoringDispatcher(server.virtualization_type)	
			except Exception as e:
				XmlRpcClient.sendAsyncMonitoringActionStatus(action.id,"FAILED",str(e))
				MonitoringDispatcher.logger.error(str(e))	
				return

			try:
				#Send async notification
				XmlRpcClient.sendAsyncMonitoringActionStatus(action.id,"ONGOING","")
				MonitoringDispatcher.logger.debug("After sending ongoing")	
				MonitoringDispatcher.__dispatchAction(dispatcher,action,server)	
			except Exception as e:
				MonitoringDispatcher.logger.error(str(e))	
				try:
					if "No route to host" in str(e):
						from settings.settingsLoader import VTAM_IP, VTAM_PORT, XMLRPC_USER, XMLRPC_PASS
						MonitoringDispatcher.logger.error("Agent cannot reach the VT AM server. Please check that the following settings are correct: https://%s:%s@%s:%s" % (XMLRPC_USER, XMLRPC_PASS, VTAM_IP, VTAM_PORT))
				except:
					pass
				raise e


	##Abstract methods definition for MonitoringDispatchers
	#Inventory
	@staticmethod
	def listActiveVMs(id,server):
		raise Exception("Abstract method cannot be called")	

