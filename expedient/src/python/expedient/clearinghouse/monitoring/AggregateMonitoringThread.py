from threading import Thread
from expedient.clearinghouse.aggregate.models import *
from expedient.clearinghouse.monitoring.XmlRpcClient import XmlRpcClient

'''
author:msune
Agent monitoring thread
'''

class AggregateMonitoringThread(Thread):
	
	__method = None
	__param = None

	'''
	Make sure Agent is up and running
	and updates status
	'''
	def __updateAggregateStatus(self, aggregate):
		try:
			XmlRpcClient.callRPCMethod('https://'+aggregate.client.username+':'+aggregate.client.password+'@'+aggregate.client.url[8:],"ping", "hello")
			aggregate.available = True
			aggregate.save()
		except Exception as e:
			#If fails for some reason mark as unreachable
			print e
			aggregate.available = False
			aggregate.save()
		
	@staticmethod
	def monitorAggregateInNewThread(param):
		thread = AggregateMonitoringThread()	
		thread.startMethod(param)
		return thread

	def startMethod(self,param):
		self.__method = self.__updateAggregateStatus 
		self.__param = param
		self.start()

	def run(self):	
		self.__method(self.__param)			
