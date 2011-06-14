import sys
from xen.XendManager import XendManager
from monitoring.MonitoringDispatcher import MonitoringDispatcher
from communications.XmlRpcClient import XmlRpcClient

'''
	@author: msune

	XenMonitoringDispatcher routines
'''

class XenMonitoringDispatcher(MonitoringDispatcher):

	##Monitoring routines
	@staticmethod
	def listActiveVMs(id,server):
		try:		
			doms = XendManager.retrieveActiveDomainsByUUID()
			XmlRpcClient.sendAsyncMonitoringActiveVMsInfo(id,"SUCCESS",doms,server)

		except Exception as e:
			#Send async notification
			XmlRpcClient.sendAsyncMonitoringActionStatus(id,"FAILED",str(e))
			#TODO improve this trace
			print e
			return
		
