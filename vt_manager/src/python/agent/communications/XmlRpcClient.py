import xmlrpclib
import threading
from utils.xml.vtRspecInterface import rspec, server_type, virtual_machine_type
from utils.XmlUtils import *
from utils.Logger import Logger
from mySettings import *

class XmlRpcClient:

	logger = Logger.getLogger()

	##Provisioning
	@staticmethod
	def __craftProvisioningResponseXml(actionId,status,description):
		rspec = XmlUtils.getEmptyProvisioningResponseObject()
		
		rspec.response.provisioning.action[0].id = actionId
		rspec.response.provisioning.action[0].status = status
		rspec.response.provisioning.action[0].description = description
		return XmlCrafter.craftXML(rspec) 


	@staticmethod
	def sendAsyncProvisioningActionStatus(actionId,status,description):
		XmlRpcClient.logger.debug("Sending asynchronous "+status+" provisioning message to: "+threading.current_thread().callBackURL)
		server = xmlrpclib.Server(threading.current_thread().callBackURL)
		XmlRpcClient.logger.debug(XmlRpcClient.__craftProvisioningResponseXml(actionId,status,description))
		server.sendAsync(XmlRpcClient.__craftProvisioningResponseXml(actionId,status,description))
		XmlRpcClient.logger.debug("Sent ("+threading.current_thread().callBackURL+")")

	##Monitoring
	@staticmethod
	def __craftMonitoringResponseXml(actionId,status,description):
	
		rspec = XmlUtils.getEmptyMonitoringResponseObject()
		
		rspec.response.monitoring.action[0].id = actionId
		rspec.response.monitoring.action[0].type_ = "listActiveVMs"
		rspec.response.monitoring.action[0].status = status
		rspec.response.monitoring.action[0].description = description
		return XmlCrafter.craftXML(rspec) 

	@staticmethod
	def __craftMonitoringActiveVMsInfoResponseXml(actionId,status,vms,serverInfo,VmStatus=None):
	
		rspec = XmlUtils.getEmptyMonitoringResponseObject()
		
		rspec.response.monitoring.action[0].id = actionId
		rspec.response.monitoring.action[0].status = status
		rspec.response.monitoring.action[0].type_ = "listActiveVMs"
		
		server = server_type()
		rspec.response.monitoring.action[0].server = server
		server.name = serverInfo.name
		server.id = serverInfo.id
		server.uuid = serverInfo.uuid
		
		for dom in vms:
			vm = virtual_machine_type()
			vm.uuid = dom[0]
			vm.name = dom[1]
			vm.status = VmStatus
			server.virtual_machines.append(vm)

		return XmlCrafter.craftXML(rspec) 
	
	

	@staticmethod
	def sendAsyncMonitoringActionStatus(actionId,status,description):
		XmlRpcClient.logger.debug("Sending asynchronous "+status+" monitoring message to: "+threading.current_thread().callBackURL)
		server = xmlrpclib.Server(threading.current_thread().callBackURL)
		XmlRpcClient.logger.debug(XmlRpcClient.__craftMonitoringResponseXml(actionId,status,description))
		server.sendAsync(XmlRpcClient.__craftMonitoringResponseXml(actionId,status,description))
		XmlRpcClient.logger.debug("Sent ("+threading.current_thread().callBackURL+")")

	@staticmethod
	def sendAsyncMonitoringActiveVMsInfo(actionId,status,vms,serverInfo):
		XmlRpcClient.logger.debug("Sending asynchronous "+status+" monitoring message to: "+threading.current_thread().callBackURL)
		server = xmlrpclib.Server(threading.current_thread().callBackURL)
		XmlRpcClient.logger.debug(XmlRpcClient.__craftMonitoringActiveVMsInfoResponseXml(actionId,status,vms,serverInfo))
		server.sendAsync(XmlRpcClient.__craftMonitoringActiveVMsInfoResponseXml(actionId,status,vms,serverInfo))
		XmlRpcClient.logger.debug("Sent ("+threading.current_thread().callBackURL+")")

	@staticmethod
	def sendAsyncMonitoringLibvirtVMsInfo(actionId,status,vms,VmStatus):
		#TODO: HARDCODED!!
		XmlRpcClient.logger.debug("Sending asynchronous "+status+" monitoring message to: VM Manager")
                serverInfo = server_type()
                serverInfo.virtualization_type = 'xen'
		#Trying to craft VM Manager URL
		server = xmlrpclib.Server('https://%s:%s@%s:%s/xmlrpc/agent'%(XMLRPC_USER,XMLRPC_PASS,VTAM_IP,VTAM_PORT))	
		#XXX:This direction works
		#server = xmlrpclib.Server('https://xml:rpc@10.216.140.11:8445/xmlrpc/agent')
		server.sendAsync(XmlRpcClient.__craftMonitoringActiveVMsInfoResponseXml(actionId,status,vms,serverInfo,VmStatus))
