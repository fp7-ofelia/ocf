from threading import Thread
from vt_manager.models import *
from vt_manager.communication.XmlRpcClient import XmlRpcClient

'''
author:msune
Agent monitoring thread
'''

class AgentMonitoringThread(Thread):
	
	__method = None
	__param = None

	'''
	Make sure Agent is up and running
	and updates status
	'''
	def __updateAgentStatus(self, server):
		try:
			print "LLALA"
			XmlRpcClient.callRPCMethod(server.getAgentURL(),"ping", "hola")
			server.setAvailable(True)
			server.save()
		except Exception as e:
			#If fails for some reason mark as unreachable
			print "HAY EXCEPCION"
			print e
			server.setAvailable(False)
			server.save()
		
	@staticmethod
	def monitorAgentInNewThread(param):
		thread = AgentMonitoringThread()	
		thread.startMethod(param)
		return thread

	def startMethod(self,param):
		self.__method = self.__updateAgentStatus 
		self.__param = param
		self.start()

	def run(self):	
		self.__method(self.__param)			
