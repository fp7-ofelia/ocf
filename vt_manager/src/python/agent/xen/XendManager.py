import os
import sys
import shutil
import subprocess
import libvirt
import time

from xen.provisioning.HdManager import HdManager

'''
	@author: msune

	Xend manager; handles Xend calls through libvirt library
'''
OXA_XEN_STOP_STEP_SECONDS=20
OXA_XEN_STOP_MAX_SECONDS=200
OXA_XEN_REBOOT_WAIT_TIME=20
OXA_XEN_CREATE_WAIT_TIME=2

class XendManager(object):

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
	def retrieveActiveDomainsByUUID():
		conn = XendManager.__getROConnection()
 
		domainIds = conn.listDomainsID()
		doms = list()

		for dId in domainIds:
			#Skip domain0
			if dId == 0:
				continue
	
			domain = conn.lookupByID(dId)
			doms.append(domain.UUIDString())

		return doms 

		

	#Provisioning routines
	@staticmethod
	def startDomain(vm):
		#Getting connection
		conn = XendManager.__getConnection()

		xmlConf = conn.domainXMLFromNative('xen-xm', open(HdManager.getConfigFilePath(vm),'r').read(), 0) 

		conn.createXML(xmlConf,0)	

		#Old way
		#subprocess.call(['/usr/sbin/xm','create',XendManager.sanitize_arg(HdManager.getConfigFilePath(vm))])
		
		time.sleep(OXA_XEN_CREATE_WAIT_TIME)

		if not XendManager.isVmRunning(vm.name):
			#TODO: add more info to exception
			raise Exception("Could not start VM")

	@staticmethod
	def stopDomain(vm):
		#If is not running skip
		if not XendManager.isVmRunning(vm.name):
			return	

		dom = XendManager.__getDomainByVmName(XendManager.__getConnection(),vm.name)
		
		#Attemp to be smart and let S.O. halt himself
		dom.shutdown()	
		
		waitTime=0
		while ( waitTime < OXA_XEN_STOP_MAX_SECONDS ) :
			if not XendManager.isVmRunning(vm.name):
				return	
			waitTime +=OXA_XEN_STOP_STEP_SECONDS
			time.sleep(OXA_XEN_STOP_STEP_SECONDS)

		#Let's behave impatiently
		dom.destroy()
		
		time.sleep(OXA_XEN_STOP_STEP_SECONDS)
	
		if XendManager.isVmRunning(vm.name):
			raise Exception("Could not stop domain")

	@staticmethod
	def rebootDomain(vm):
		dom = XendManager.__getDomainByVmName(XendManager.__getConnection(),vm.name)
		dom.reboot(0)
		time.sleep(OXA_XEN_REBOOT_WAIT_TIME)
		if not XendManager.isVmRunning(vm.name):
			raise Exception("Could not reboot domain (maybe rebooted before MINIMUM_RESTART_TIME?). Domain will remain in stop state")

		

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
	
