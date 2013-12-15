from communications.XmlRpcClient import XmlRpcClient
from monitoring.MonitoringDispatcher import MonitoringDispatcher
from utils.Logger import Logger
from xen.XendManager import XendManager

"""
	@author: msune

	XenMonitoringDispatcher routines
"""

class XenMonitoringDispatcher(MonitoringDispatcher):
	
	logger = Logger.getLogger()
	
	# Monitoring routines
	@staticmethod
	def list_active_vms(id,server):
		try:		
			doms = XendManager.retrieveActiveDomainsByUUID()
			XmlRpcClient.sendAsyncMonitoringActiveVMsInfo(id,"SUCCESS",doms,server)
		except Exception as e:
			#Send async notification
			XmlRpcClient.sendAsyncMonitoringActionStatus(id,"FAILED",str(e))
			XenMonitoringDispatcher.logger.error(str(e))
			return
	