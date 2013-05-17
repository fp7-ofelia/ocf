from threading import Thread
from vt_manager.controller.monitoring.StatisticsMonitor import StatisticsMonitor
'''
	author:msune
	Agent monitoring thread
'''

MONITORING_INTERVAL_FACTOR=0.95

class StatisticsMonitoringThread(Thread):
	
	__method = None

	'''
	Make sure Agent is up and running
	and updates status
	'''
		

	def __updateStatisticsStatus(self):
		try:
			StatisticsMonitor.updateStatistics()
		except Exception as e:
			#If fails for some reason mark as unreachable
			print e
		
	@staticmethod
	def monitorStatisticsInNewThread():
		thread = StatisticsMonitoringThread()	
		thread.startMethod()
		return thread

	def startMethod(self):
		self.__method = self.__updateStatisticsStatus
		self.start()

	def run(self):	
		self.__method()			
