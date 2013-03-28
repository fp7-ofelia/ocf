#!/usr/bin/python
import sys,os
import pprint
from provisioning.ProvisioningDispatcher import ProvisioningDispatcher 
from monitoring.MonitoringDispatcher import MonitoringDispatcher
from monitoring.LibvirtMonitoring import LibvirtMonitor 
from communications.XmlRpcServer import XmlRpcServer
from utils.ServiceThread import ServiceThread
from utils.XmlUtils import *
from utils.xml.vtRspecInterface import rspec
from settings.settingsLoader import OXA_LOG
from utils.Logger import Logger
'''
	@author: msune

	OXA: Ofelia XEN Agent. 

'''

logger = Logger.getLogger()

''' Usage message '''
def usage():
	# return "\nOXA: Ofelia XEN Agent utility. This utility expects as an argument an XML query, and performs\nXEN VM provisioning and monitoring operations. \n\n Usage:\n \t OXA.py xmlQuery"
	return "TODO" #TODO
	
''' Argument checking '''
def checkArgs():
	if len(sys.argv) > 2 :
		raise Exception("Illegal number of arguments\n\n"+usage())



''' Redirect stdout and stderr '''
def redirectStdinStderr():
	output = open(OXA_LOG+"output.log",'a+',0)
	error = open(OXA_LOG+"error.log",'a+',0)

	sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
	sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', 0)

	os.dup2(output.fileno(), sys.stdout.fileno())
	os.dup2(error.fileno(), sys.stderr.fileno())

	output.close()
	error.close()	

''' Restore stdout and stderr '''
def restoreStdinStderr():
	sys.stdout = sys.__stdout__
	sys.stdout = sys.__stderr__	

''' Deamonizes execution '''
def forkAndExitFather():

	child_pid = os.fork()

    	if child_pid == 0:
		#Redirect stdout and stderr to log files
		redirectStdinStderr()
        	return	
    	else:
		fp = open('/var/run/OfeliaAgent.pid', 'w')
        	fp.write(str(child_pid))
        	fp.flush()
		fp.close()
         	sys.exit()	


def processXmlQuery(notificationCallBackUrl,xml):

	#TODO:Authentication
			
	#Parse
	try:
#		logger.debug(xml)
		rspecValue = XmlParser.parseXML(xml)
	except Exception as e:
		logger.error(e)	
		raise e

	#For each type of action call appropiate method in a new thread
	if(rspecValue.query.provisioning != None):
		ServiceThread.startMethodInNewThread(ProvisioningDispatcher.processProvisioning,rspecValue.query.provisioning,notificationCallBackUrl)

	if(rspecValue.query.monitoring != None):
		ServiceThread.startMethodInNewThread(MonitoringDispatcher.processMonitoring,rspecValue.query.monitoring,notificationCallBackUrl)



'''Main routine, opening the XML-RPC server'''
def main():
	logger.info("OFELIA XEN Agent")	
	
	checkArgs()

	#If -b is passed, demonize it 
	if len(sys.argv) == 2 and sys.argv[1] == "-b" :
		forkAndExitFather()

	##testing	
	#processXmlQuery("https://147.83.206.92:9229",1,sys.argv[1])
	#print "Main ends..." 
	logger.debug("Starting LibvirtMonitoring...")
	try:
		LibvirtMonitor.initialize()
	except Exception as e:
		logger.debug("LibvirtMonitoring failed: %s" % (e))
	logger.debug('LibvirtMonitoring started')
	#Engage XMLRPC
	logger.debug("Trying to engage XMLRPC server...")
	XmlRpcServer.createInstanceAndEngage(processXmlQuery)	
	logger.debug("This is unreachable!")	

#Calling main
if __name__ == "__main__":
    main()
