import os                                                                     
import sys                                                                    

from controller.dispatchers.provisioningdispatcher import ProvisioningDispatcher
from controller.dispatchers.provisioningresponsedispatcher import ProvisioningResponseDispatcher
from controller.dispatchers.monitoringresponsedispatcher import MonitoringResponseDispatcher
from controller.dispatchers.informationdispatcher import InformationDispatcher

from utils.servicethread import *                                      

import threading                                                                             

class DispatcherLauncher():
	
	@staticmethod
	def processXmlResponse(rspec):
		if not rspec.response.provisioning == None:
			ServiceThread.startMethodInNewThread(ProvisioningResponseDispatcher.processResponse, rspec)
		if not rspec.response.monitoring == None:
			ServiceThread.startMethodInNewThread(MonitoringResponseDispatcher.processResponse, rspec)

	@staticmethod
	def processXmlQuery(rspec):
		#check if provisioning / monitoring / etc
		if not rspec.query.provisioning == None :
			ServiceThread.startMethodInNewThread(ProvisioningDispatcher.processProvisioning,rspec.query.provisioning, threading.currentThread().callBackURL)
    
	@staticmethod
	def processInformation(remoteHashValue, projectUUID ,sliceUUID):
		return InformationDispatcher.listResources(remoteHashValue, projectUUID, sliceUUID)
