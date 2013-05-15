from threading import Thread
import random 
from vt_manager.models.VTServer import VTServer
from vt_manager.communication.XmlRpcClient import XmlRpcClient
from vt_manager.controller.monitoring.VMMonitor import VMMonitor
'''
	author:msune
	Agent monitoring thread
'''

MONITORING_INTERVAL_FACTOR=0.95

class StatisticsMonitoringThread(Thread):
	
	__method = None
	__param = None

	'''
	Make sure Agent is up and running
	and updates status
	'''
		

	def __updateStatistics(self):
		try:
			StatisticsMonitor.updateStatistics()
		except Exception as e:
			#If fails for some reason mark as unreachable
			print e
		
	@staticmethod
	def monitorAgentInNewThread(param):
		thread = StatisticsMonitoringThread()	
		thread.startMethod(param)
		return thread

	def startMethod(self,param):
		self.__method = self.__updateStatisticsStatus 
		self.__param = param
		self.start()

	def run(self):	
		self.__method(self.__param)			
