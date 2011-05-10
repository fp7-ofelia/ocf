import xmlrpclib
import threading
from utils.xml.vtRspecInterface import rspec, server_type, virtual_machine_type
from utils.XmlUtils import *

class XmlRpcClient:

	##Provisioning
	@staticmethod
	def __craftProvisioningResponseXml(actionId,status,description):
	
		rspec = XmlUtils.getProvisioningEmptyResponseObject()
		
		rspec.response.provisioning.action[0].id = actionId
		rspec.response.provisioning.action[0].status = status
		rspec.response.provisioning.action[0].description = description
		return XmlCrafter.craftXML(rspec) 


	@staticmethod
	def sendAsyncProvisioningActionStatus(actionId,status,description):
		server = xmlrpclib.Server(threading.current_thread().callBackURL)
		print XmlRpcClient.__craftProvisioningResponseXml(actionId,status,description)
		server.sendAsync(XmlRpcClient.__craftResponseXml(actionId,status,description))

	##Monitoring
	@staticmethod
	def __craftMonitoringResponseXml(actionId,status,description):
	
		rspec = XmlUtils.getEmptyMonitoringResponseObject()
		
		rspec.response.monitoring.action[0].id = actionId
		rspec.response.monitoring.action[0].status = status
		rspec.response.monitoring.action[0].description = description
		return XmlCrafter.craftXML(rspec) 

	@staticmethod
	def __craftMonitoringActiveVMsInfoResponseXml(actionId,status,vms,serverInfo):
	
		rspec = XmlUtils.getEmptyMonitoringResponseObject()
		
		rspec.response.monitoring.action[0].id = actionId
		rspec.response.monitoring.action[0].status = status
		
		server = server_type()
		rspec.response.monitoring.action[0].server = server
		server.name = serverInfo.name
		server.id = serverInfo.id
		server.uuid = serverInfo.uuid
	
		for uuid in vms:
			vm = virtual_machine_type()
			vm.uuid = uuid
			server.virtual_machines.append(vm)	
	
		return XmlCrafter.craftXML(rspec) 


	@staticmethod
	def sendAsyncMonitoringActionStatus(actionId,status,description):
		server = xmlrpclib.Server(threading.current_thread().callBackURL)
		print XmlRpcClient.__craftMonitoringResponseXml(actionId,status,description)
		server.sendAsync(XmlRpcClient.__craftResponseXml(actionId,status,description))

	@staticmethod
	def sendAsyncMonitoringActiveVMsInfo(actionId,status,vms,serverInfo):

		server = xmlrpclib.Server(threading.current_thread().callBackURL)
		print XmlRpcClient.__craftMonitoringActiveVMsInfoResponseXml(actionId,status,vms,serverInfo)
		server.sendAsync(XmlRpcClient.__craftMonitoringActiveVMsInfoResponseXml(actionId,status,vms,serverInfo))


