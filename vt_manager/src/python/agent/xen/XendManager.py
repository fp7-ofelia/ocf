import os
import sys
import shutil
import subprocess
import libvirt

from xen.provisioning.HdManager import HdManager

'''
	@author: msune

	Xend manager; handles Xend calls through libvirt library
'''
OXA_XEN_STOP_STEP_SECONDS=20
OXA_XEN_STOP_MAX_SECONDS=200

class XendManager(object):
	
	@staticmethod
	def __getROConnection():
		return libvirt.openReadOnly(None)
	
	@staticmethod
	def __getConnection():
		return libvirt.open(None)
		
	@staticmethod
	def isVmRunning(name):
		conn = XendManager.__getROConnection() 
		try:
			dom = conn.lookupByName(name)	
			return dom.isActive()
		except Exception as e:
			return False

	@staticmethod
	def __getDomainByVmName(conn,name):
		return conn.lookupByName(name)	

	@staticmethod
	def startDomain(vm):
		#Getting connection
		subprocess.call(['/usr/sbin/xm','create',HdManager.getConfigFilePath(vm)])
		if not XendManager.isVmRunning(vm.name):
			#TODO: add more info to exception
			raise Exception("Could not start VM")

	@staticmethod
	def stopDomain(vm):
		dom = XendManager.__getDomainByVmName(XendManager.__getConnection(),vm.name)
		
		#Attemp to be smart and let S.O. halt himself
		dom.shutdown()	
		
		waitTime=0
		while ( waitTime < OXA_XEN_STOP_MAX_SECONDS ) :
			if not XendManager.isVmRunning(vm.name):
				return	
			waitTime +=OXA_XEN_STOP_STEP_SECONDS

		#Let's behave impatiently
		dom.destroy()
	
		if XendManager.isVmRunning(vm.name):
			raise Exception("Could not stop domain")

	@staticmethod
	def rebootDomain(vm):
		dom = XendManager.__getDomainByVmName(XendManager.__getConnection(),vm.name)
		dom.reboot(0)

	''' XXX: To be implemented '''	
	@staticmethod
	def pauseDomain(vm):
		dom = XendManager.__getDomainByVmName(XendManager.__getConnection(),vm.name)
		#XXX		
		raise Exception("Not implemented")	
	@staticmethod
	def resumeDomain(vm):
		dom = XendManager.__getDomainByVmName(XendManager.__getConnection(),vm.name)
		#XXX
		raise Exception("Not implemented")	
	
