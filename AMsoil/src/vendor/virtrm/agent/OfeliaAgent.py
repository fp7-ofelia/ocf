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
from settings.loader import OXA_LOG
from utils.Logger import Logger

'''
	@author: msune

	OXA: Ofelia XEN Agent. 

'''

logger = Logger.getLogger()

def usage():
	"""
	Usage message
	"""
	# TODO
	# return "\nOXA: Ofelia XEN Agent utility. This utility expects as an argument an XML query, and performs\nXEN VM provisioning and monitoring operations. \n\n Usage:\n \t OXA.py xmlQuery"
	return "TODO"
	
def check_args():
	"""
	Argument checking
	"""
	if len(sys.argv) > 2 :
		raise Exception("Illegal number of arguments\n\n"+usage())

def redirect_stdin_stderr():
	"""
	Redirect stdout and stderr
	"""
	output = open(OXA_LOG + "output.log", 'a+', 0)
	error = open(OXA_LOG + "error.log", 'a+', 0)
	sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
	sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', 0)
	os.dup2(output.fileno(), sys.stdout.fileno())
	os.dup2(error.fileno(), sys.stderr.fileno())
	output.close()
	error.close()	

def restore_stdin_stderr():
	"""
	Restore stdout and stderr
	"""
	sys.stdout = sys.__stdout__
	sys.stdout = sys.__stderr__	

def fork_and_exit_father():
	"""
	Daemonizes execution
	"""
	child_pid = os.fork()
    	if child_pid == 0:
		#Redirect stdout and stderr to log files
		redirect_stdin_stderr()
        	return	
    	else:
		fp = open('/var/run/OfeliaAgent.pid', 'w')
        	fp.write(str(child_pid))
        	fp.flush()
		fp.close()
         	sys.exit()	

def process_query(notificationCallBackUrl,xml):
	# TODO:Authentication	
	# Parse
	try:
		rspec_value = XmlParser.parseXML(xml)
	except Exception as e:
		logger.error(e)	
		raise e
	# For each type of action call appropriate method in a new thread,
	# necessary in order to get the callback from it to return results
	if rspec_value.query.provisioning != None:
		ServiceThread.startMethodInNewThread(ProvisioningDispatcher.processProvisioning,rspec_value.query.provisioning,notificationCallBackUrl)
	if rspec_value.query.monitoring != None:
		ServiceThread.startMethodInNewThread(MonitoringDispatcher.processMonitoring,rspec_value.query.monitoring,notificationCallBackUrl)

def main():
	"""
	Main routine, opening the XML-RPC server
	"""
	logger.info("OFELIA XEN Agent")	
	check_args()
	# If -b is passed, demonize it 
	if len(sys.argv) == 2 and sys.argv[1] == "-b" :
		fork_and_exit_father()
	# Testing	
	# process_query("https://147.83.206.92:9229",1,sys.argv[1])
	# logger.debug("Main ends...")
	logger.debug("Starting LibvirtMonitoring...")
	try:
		LibvirtMonitor.initialize()
	except Exception as e:
		logger.debug("LibvirtMonitoring failed: %s" % (e))
	logger.debug('LibvirtMonitoring started')
	# Engage XMLRPC
	logger.debug("Trying to engage XMLRPC server...")
	XmlRpcServer.createInstanceAndEngage(process_query)	
	logger.debug("This is unreachable!")	

# Calling main
if __name__ == "__main__":
    main()
