import sys
from xen.XendManager import XendManager
from monitoring.MonitoringDispatcher import MonitoringDispatcher
from communications.XmlRpcClient import XmlRpcClient
from utils.Logger import Logger

'''
	@author: msune

	XenMonitoringDispatcher routines
'''

class XenMonitoringDispatcher(MonitoringDispatcher):
	
	logger = Logger.getLogger()
	
	##Monitoring routines
	@staticmethod
	def listActiveVMs(id,server):
		try:		
			doms = XendManager.retrieveActiveDomainsByUUID()
			XmlRpcClient.sendAsyncMonitoringActiveVMsInfo(id,"SUCCESS",doms,server)

		except Exception as e:
			#Send async notification
			XmlRpcClient.sendAsyncMonitoringActionStatus(id,"FAILED",str(e))
			XenMonitoringDispatcher.logger.error(str(e))
			return
		
