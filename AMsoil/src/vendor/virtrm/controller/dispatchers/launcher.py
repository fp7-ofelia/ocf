import os                                                                     
import sys                                                                    

from controller.dispatchers.information.query import InformationDispatcher
from controller.dispatchers.monitoring.response import MonitoringResponseDispatcher
from controller.dispatchers.provisioning.query import ProvisioningDispatcher
from controller.dispatchers.provisioning.response import ProvisioningResponseDispatcher
from utils.servicethread import *                                      

import threading                                                                             

class DispatcherLauncher():
	
	@staticmethod
	def process_response(rspec):
		"""
		Process XML response.
		"""
		if not rspec.response.provisioning == None:
			ServiceThread.startMethodInNewThread(ProvisioningResponseDispatcher.process, rspec)
		if not rspec.response.monitoring == None:
			ServiceThread.startMethodInNewThread(MonitoringResponseDispatcher.process, rspec)

	@staticmethod
	def process_query(rspec):
		"""
		Process XML query.
		"""
		# Check if provisioning / monitoring / etc
		if not rspec.query.provisioning == None :
			ServiceThread.startMethodInNewThread(ProvisioningDispatcher.process,
												rspec.query.provisioning, threading.currentThread().callBackURL)
    
	@staticmethod
	def process_information(remote_hash_value, project_uuid, slice_uuid):
		"""
		Process information received by listResources.
		"""
		return InformationDispatcher.listResources(remote_hash_value, project_uuid, slice_uuid)
