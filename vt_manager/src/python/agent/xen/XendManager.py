import os
import sys
import shutil
import subprocess
import libvirt
import time
from threading import Thread, Lock

from xen.provisioning.HdManager import HdManager
from utils.Logger import Logger


'''
	@author: msune

	Xend manager; handles Xend calls through libvirt library
'''
OXA_XEN_STOP_STEP_SECONDS=6
OXA_XEN_STOP_MAX_SECONDS=100
OXA_XEN_REBOOT_WAIT_TIME=20
OXA_XEN_CREATE_WAIT_TIME=2
OXA_XEN_MAX_DUPLICATED_NAME_VMS=999999

class XendManager(object):
	
	_mutex = Lock() 
	_xendConnection = None #NEVER CLOSE IT 
	_xendConnectionRO = None #Not really used 
	logger = Logger.getLogger()

	#Shell util
	@staticmethod
	def sanitize_arg(arg):
		return arg.replace('\\','\\\\').replace('\'','\\\'').replace(' ','\ ') 
	
	@staticmethod
	def __getROConnection():
		#return libvirt.openReadOnly(None)
		return XendManager.__getConnection() #By-passed
	@staticmethod
	def __getConnection():
		with XendManager._mutex:
			if XendManager._xendConnection is None:
				XendManager._xendConnection = libvirt.open(None)
			return XendManager._xendConnection
	
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

		with open(HdManager.getConfigFilePath(vm),'r') as openConfig: 
			xmlConf = conn.domainXMLFromNative('xen-xm', openConfig.read(), 0) 

		#con = libvirt.open('xen:///')
		#dom = con.createLinux(xmlConf,0)
				

		if XendManager.isVmRunning(vm.name) and not  XendManager.isVmRunningByUUID(vm.uuid):
			#Duplicated name; trying to find an Alias
			newVmName = XendManager.__findAliasForDuplicatedVmName(vm)
			command_list = ['/usr/sbin/xm', 'create', 'name=' + newVmName, XendManager.sanitize_arg(HdManager.getConfigFilePath(vm))]
			process = subprocess.Popen(command_list, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			out, err = process.communicate()
		else:	
			try:
				#Try first using libvirt call
				#XendManager.logger.warning('creating vm using python-libvirt methods')
                                #XendManager.logger.warning(xmlConf)
				#conn.createXML(xmlConf,0)
				#XendManager.logger.warning(XendManager.sanitize_arg(HdManager.getConfigFilePath(vm)))
                                #XendManager.logger.warning('created vm?')
				raise Exception("Skip") #otherwise stop is ridicously slow
			except Exception as e:
				#Fallback solution; workarounds BUG that created wrong .conf files (extra spaces that libvirt cannot parse)
				command_list = ['/usr/sbin/xm', 'create', XendManager.sanitize_arg(HdManager.getConfigFilePath(vm))]
				process = subprocess.Popen(command_list, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				out, err = process.communicate()

		time.sleep(OXA_XEN_CREATE_WAIT_TIME)

		if not XendManager.isVmRunningByUUID(vm.uuid):
			# Complete with other types of exceptions
			detailed_error = ""
			if "Not enough free memory" in err:
				detailed_error = " because there is not enough free memory in that server. Try another."
			raise Exception("Could not start VM%s" % detailed_error)

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
	
