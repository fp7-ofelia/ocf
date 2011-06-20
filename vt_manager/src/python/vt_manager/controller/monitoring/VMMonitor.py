from threading import Thread
from vt_manager.models.VTServer import VTServer
from vt_manager.communication.XmlRpcClient import XmlRpcClient
from vt_manager.communication.utils.XmlHelper import XmlHelper
from vt_manager.controller.actions.ActionController import ActionController
from vt_manager.models.Action import Action

from vt_manager.settings.settingsLoader import *

'''
	author:msune
	Encapsulates VM monitoring methods	
'''

class VMMonitor(): 
	
	@staticmethod
	def updateVMs(server):
		#Recover from the client the list of active VMs
		obj = XmlHelper.getListActiveVMsQuery()
	
		#Create new Action 
		action = ActionController.createNewAction(Action.MONITORING_SERVER_VMS_TYPE,Action.ONGOING_STATUS,server.getUUID(),"") 

			
		obj.query.monitoring.action[0].id = action.getUUID() 
		obj.query.monitoring.action[0].server.virtualization_type = server.getid = server.getVirtTech() 
		XmlRpcClient.callRPCMethod(server.getAgentURL(),"send","https://"+ROOT_USERNAME+":"+ROOT_PASSWORD+"@"+VTAM_IP+":"+VTAM_PORT,0,server.agentPassword,XmlHelper.craftXmlClass(obj))
		
		


