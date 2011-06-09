from threading import Thread
from vt_manager.models.VTServer import VTServer
from vt_manager.communication.XmlRpcClient import XmlRpcClient

'''
	author:msune
	Encapsulates VM monitoring methods	
'''

class VMMonitor(): 
	
	@staticmethod
	def updateVMs(server):
		#Recover from the client the list of active VMs
		pass	
		XmlRpcClient.callRPCMethod(server.getAgentURL(),"send", "hola")
		
		


