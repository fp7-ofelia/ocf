from vt_manager.models import *
import uuid
import AgentMonitoringThread
import time
from threading import *
from vt_manager.settings import MONITORING_INTERVAL 

'''
author:msune
Monitoring thread implementation
'''

class BackgroundMonitor():
	
	'''
	Updates server status
	'''
	@staticmethod
	def __monitorServers():
			
		for server in VTServer.objects.all():
			AgentMonitoringThread.monitorAgentInNewThread(server)				
		#Wait for threads
		for thread in threading.enumerate():
			if thread is not threading.currentThread():
				thread.join()

	@staticmethod
	def monitor(): 
		
		#Main monitoring loop
		while True:
			BackgroundMonitor.__monitorServers()	
			time.sleep(MONITORING_INTERVAL)					
		
