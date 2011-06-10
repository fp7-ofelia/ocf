from threading import Thread
from vt_manager.models.VTServer import VTServer
from vt_manager.communication.XmlRpcClient import XmlRpcClient
from vt_manager.communication.utils.XmlHelper import XmlHelper

'''
	author:msune
	Encapsulates VM monitoring methods	
'''

class VMMonitor(): 
	
	@staticmethod
	def updateVMs(server):
		#Recover from the client the list of active VMs
		obj = XmlHelper.getListActiveVMsQuery()
	
		#Add id and server 
		obj.query.monitoring.action.id = "fff"
		obj.query.monitoring.action.server.virtualization_type = server.getid = server.getVirtTech() 
		print XmlHelper.craftXml(obj)
		return 	
		XmlRpcClient.callRPCMethod(server.getAgentURL(),"send", "hola")
		
		


