from threading import Thread
from vt_manager.models.VTServer import VTServer
from vt_manager.communication.XmlRpcClient import XmlRpcClient
from vt_manager.communication.utils.XmlHelper import XmlHelper
from vt_manager.controller.actions.ActionController import ActionController
from vt_manager.models.Action import Action
from vt_manager.utils.UrlUtils import UrlUtils

'''
	author:msune
	Encapsulates VM monitoring methods	
'''

class VMMonitor(): 
	
	@staticmethod
	def sendUpdateVMs(server):
		#Recover from the client the list of active VMs
		obj = XmlHelper.getListActiveVMsQuery()
	
		#Create new Action 
		action = ActionController.createNewAction(Action.MONITORING_SERVER_VMS_TYPE,Action.QUEUED_STATUS,server.getUUID(),"") 

			
		obj.query.monitoring.action[0].id = action.getUUID() 
		obj.query.monitoring.action[0].server.virtualization_type = server.getid = server.getVirtTech() 
		XmlRpcClient.callRPCMethod(server.getAgentURL(),"send",UrlUtils.getOwnCallbackURL(),0,server.agentPassword,XmlHelper.craftXmlClass(obj))
		
		

	@staticmethod
	def processUpdateVMsList(server,vmList):
		for vm in vmList:
			print "VM in: "+vm.uuid
		
