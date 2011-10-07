import os
import sys
import shutil
import subprocess
import libvirt
import time
from threading import Thread, Lock

from xen.provisioning.HdManager import HdManager

'''
	@author: msune

	Xend manager; handles Xend calls through libvirt library
'''
OXA_XEN_STOP_STEP_SECONDS=6
OXA_XEN_STOP_MAX_SECONDS=100
OXA_XEN_REBOOT_WAIT_TIME=20
OXA_XEN_CREATE_WAIT_TIME=2
OXA_XEN_MAX_DUPLICATED_NAME_VMS=999999

_XendManagerMutex = Lock()

class XendManager(object):
	
	_mutex = _XendManagerMutex

	#Shell util
	@staticmethod
	def sanitize_arg(arg):
		return arg.replace('\\','\\\\').replace('\'','\\\'').replace(' ','\ ') 
	
	@staticmethod
	def __getROConnection():
		return libvirt.openReadOnly(None)
	
	@staticmethod
	def __getConnection():
		return libvirt.open(None)
	
	@staticmethod
	def __getDomainByVmName(conn,name):
		return conn.lookupByName(name)	

	@staticmethod
	def __getDomainByVmUUID(conn,uuid):
		return conn.lookupByUUIDString(uuid)	

	#Monitoring	
	@staticmethod
	def isVmRunning(name):
		conn = XendManager.__getROConnection() 
		try:
			dom = conn.lookupByName(name)	
			return dom.isActive()
		except Exception as e:
			return False
	@staticmethod
	def isVmRunningByUUID(uuid):
		conn = XendManager.__getROConnection() 
		try:
			dom = conn.lookupByUUIDString(uuid)	
			return dom.isActive()
		except Exception as e:
			return False


	@staticmethod
	def retrieveActiveDomainsByUUID():
		conn = XendManager.__getROConnection()
 
		domainIds = conn.listDomainsID()
		doms = list()

		for dId in domainIds:
			#Skip domain0
			if dId == 0:
				continue
	
			domain = conn.lookupByID(dId)
			doms.append((domain.UUIDString(),domain.name()))

		return doms 

	@staticmethod
	def __findAliasForDuplicatedVmName(vm):
		with XendManager._mutex:
			#Duplicated VM name; find new temporal alias
			newVmName = vm.name
			for i in range(OXA_XEN_MAX_DUPLICATED_NAME_VMS):
				if not XendManager.isVmRunning(vm.name+"_"+str(i)):
					return str(vm.name+"_"+str(i))
								
			Exception("Could not generate an alias for a duplicated vm name.")	
			

	#Provisioning routines
	@staticmethod
	def startDomain(vm):
		#Getting connection
		conn = XendManager.__getConnection()

		xmlConf = conn.domainXMLFromNative('xen-xm', open(HdManager.getConfigFilePath(vm),'r').read(), 0) 

		if XendManager.isVmRunning(vm.name) and not  XendManager.isVmRunningByUUID(vm.uuid):
			#Duplicated name; trying to find an Alias
			newVmName = XendManager.__findAliasForDuplicatedVmName(vm)
			subprocess.call(['/usr/sbin/xm','create','name='+newVmName,XendManager.sanitize_arg(HdManager.getConfigFilePath(vm))])
		else:	
			try:
				#Try first using libvirt call
				#conn.createXML(xmlConf,0)
				raise Exception("Skip") #otherwise stop is ridicously slow
			except Exception as e:
				#Fallback solution; workarounds BUG that created wrong .conf files (extra spaces that libvirt cannot parse)
				subprocess.call(['/usr/sbin/xm','create',XendManager.sanitize_arg(HdManager.getConfigFilePath(vm))])
			
		time.sleep(OXA_XEN_CREATE_WAIT_TIME)

		if not XendManager.isVmRunningByUUID(vm.uuid):
			#TODO: add more info to exception
			raise Exception("Could not start VM")

	@staticmethod
	def stopDomain(vm):
		#If is not running skip
		if not XendManager.isVmRunningByUUID(vm.uuid):
			return	

		#dom = XendManager.__getDomainByVmName(XendManager.__getConnection(),vm.name)
		dom = XendManager.__getDomainByVmUUID(XendManager.__getConnection(),vm.uuid)
		
		#Attemp to be smart and let S.O. halt himself
		dom.shutdown()	
		
		waitTime=0
		while ( waitTime < OXA_XEN_STOP_MAX_SECONDS ) :
			if not XendManager.isVmRunningByUUID(vm.uuid):
				return	
			waitTime +=OXA_XEN_STOP_STEP_SECONDS
			time.sleep(OXA_XEN_STOP_STEP_SECONDS)

		#Let's behave impatiently
		dom.destroy()
		
		time.sleep(OXA_XEN_REBOOT_WAIT_TIME)
	
		if XendManager.isVmRunningByUUID(vm.uuid):
			raise Exception("Could not stop domain")

	@staticmethod
	def rebootDomain(vm):
		#dom = XendManager.__getDomainByVmName(XendManager.__getConnection(),vm.name)
		dom = XendManager.__getDomainByVmUUID(XendManager.__getConnection(),vm.uuid)
		dom.reboot(0)
		time.sleep(OXA_XEN_REBOOT_WAIT_TIME)
		if not XendManager.isVmRunningByUUID(vm.uuid):
			raise Exception("Could not reboot domain (maybe rebooted before MINIMUM_RESTART_TIME?). Domain will remain in stop state")

		

	''' XXX: To be implemented '''	
	@staticmethod
	def pauseDomain(vm):
		#XXX		
		raise Exception("Not implemented")	
	@staticmethod
	def resumeDomain(vm):
		#XXX
		raise Exception("Not implemented")	
	
