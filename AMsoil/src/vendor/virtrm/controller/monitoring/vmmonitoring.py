from threading import Thread

from communication.xmlrpcclient import XmlRpcClient
from utils.xmlhelper import XmlHelper
from controller.actions.actioncontroller import ActionController
from utils.action import Action
from utils.urlutils import UrlUtils

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
		from resources.virtualmachine import VirtualMachine
		for vm in server.getChildObject().vms:
			isUp = False
			for iVm in vmList:
				if iVm.uuid == vm.uuid:
					#Is running
					vm.setState(VirtualMachine.RUNNING_STATE)
					isUp = True
					break

			if isUp:
				continue

			#Is not running
			vm.setState(VirtualMachine.STOPPED_STATE)

	@staticmethod
	def processUpdateVMsListFromCallback(vmUUID,state,rspec):
		from resources.virtualmachine import VirtualMachine
		from sqlalchemy import create_engine
		from sqlalchemy.orm import scoped_session, sessionmaker
		from utils.commonbase import ENGINE

	        db_engine = create_engine(ENGINE, pool_recycle=6000)
        	db_session_factory = sessionmaker(autoflush=True, autocommit=True, bind=db_engine, expire_on_commit=False)
        	db_session = scoped_session(db_session_factory)
		
		try:
			VM = db_session.query(VirtualMachine).filter(VirtualMachine.uuid = vmUUID).first()

		except Exception as e:
			raise e

		if state == 'Started':
			VM.setState(VirtualMachine.RUNNING_STATE)
		elif state == 'Stopped':
			VM.setState(VirtualMachine.STOPPED_STATE)
		else:
			VM.setState(VirtualMachine.UNKNOWN_STATE)
		
		#XXX: Maybe there better palces to send to expedient this update state...	
		XmlRpcClient.callRPCMethod(VM.getCallBackURL(), "sendAsync", XmlHelper.craftXmlClass(rspec))				
