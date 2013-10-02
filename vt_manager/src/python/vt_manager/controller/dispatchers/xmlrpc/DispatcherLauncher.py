from django.http import *                                                     
import os                                                                     
import sys                                                                    
from vt_manager.controller.dispatchers.xmlrpc.ProvisioningDispatcher import ProvisioningDispatcher
from vt_manager.controller.dispatchers.xmlrpc.ProvisioningResponseDispatcher import ProvisioningResponseDispatcher
from vt_manager.controller.dispatchers.xmlrpc.MonitoringResponseDispatcher import MonitoringResponseDispatcher
from vt_manager.controller.dispatchers.xmlrpc.InformationDispatcher import InformationDispatcher
from vt_manager.communication.utils import *                                  
from vt_manager.utils.ServiceThread import *                                      
from vt_manager.common.rpc4django import rpcmethod                                       
from vt_manager.common.rpc4django import *                                               
import threading                                                                             

#XXX: Sync Thread for VTPlanner
from vt_manager.utils.SyncThread import *

class DispatcherLauncher():
	
	@staticmethod
	def processXmlResponse(rspec):
		if not rspec.response.provisioning == None:
			ServiceThread.startMethodInNewThread(ProvisioningResponseDispatcher.processResponse, rspec)
		if not rspec.response.monitoring == None:
			ServiceThread.startMethodInNewThread(MonitoringResponseDispatcher.processResponse, rspec)

	@staticmethod
        def processXmlResponseSync(rspec):
                if not rspec.response.provisioning == None:
                        SyncThread.startMethodAndJoin(ProvisioningResponseDispatcher.processResponseSync, rspec)
                if not rspec.response.monitoring == None:
                        SyncThread.startMethodAndJoin(MonitoringResponseDispatcher.processResponseSync, rspec)


	@staticmethod
	def processXmlQuery(rspec):
		#check if provisioning / monitoring / etc
		if not rspec.query.provisioning == None :
			ServiceThread.startMethodInNewThread(ProvisioningDispatcher.processProvisioning,rspec.query.provisioning, threading.currentThread().callBackURL)
	
	@staticmethod    
	def processXmlQuerySync(rspec):
	    #check if provisioning / monitoring / etc
            if not rspec.query.provisioning == None :
		SyncThread.startMethodAndJoin(ProvisioningDispatcher.processProvisioningSync, rspec.query.provisioning, threading.currentThread().callBackURL)


	@staticmethod
	def processInformation(remoteHashValue, projectUUID ,sliceUUID):
		return InformationDispatcher.listResources(remoteHashValue, projectUUID, sliceUUID)
