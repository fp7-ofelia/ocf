from threading import Thread
from vt_manager.models.VTServer import VTServer
from vt_manager.communication.XmlRpcClient import XmlRpcClient
from vt_manager.controller.monitoring.VMMonitor import VMMonitor
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
			print "Pinging Agent on server %s" % server.name
			XmlRpcClient.callRPCMethod(server.getAgentURL(),"ping", "hola")
			#Server is up
 			print "Ping Agent on server %s was SUCCESSFUL!" % server.name
			if server.available == False:
				#
				VMMonitor.sendUpdateVMs(server)
				server.setAvailable(True)
				server.save()
		except Exception as e:
			#If fails for some reason mark as unreachable
			print "Could not reach server %s. Will be set as unavailable "
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
