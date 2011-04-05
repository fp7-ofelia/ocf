#!/usr/bin/python
import sys,os
import pprint
from provisioning.ProvisioningDispatcher import ProvisioningDispatcher 
from communications.XmlRpcServer import XmlRpcServer
from utils.ServiceThread import ServiceThread
from utils.XmlUtils import *
from utils.xml.vtRspecInterface import rspec
from settings import OXA_LOG

'''
	@author: msune

	OXA: Ofelia XEN Agent. 

'''

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
	sys.stdout = open(OXA_LOG+"output.log",'a')
	sys.stderr = open(OXA_LOG+"error.log",'a')

''' Restore stdout and stderr '''
def restoreStdinStderr():
	sys.stdout = sys.__stdout__
	sys.stdout = sys.__stderr__	

''' Deamonizes execution '''
def forkAndExitFather():

	child_pid = os.fork()

    	if child_pid == 0:
		#redirectStdinStderr()
        	return	
    	else:
		fp = open('/var/run/OfeliaAgent.pid', 'w')
        	fp.write(str(child_pid))
        	fp.flush()
         	sys.exit()	


def processXmlQuery(notificationCallBackUrl,amId,xml):

	#TODO:Authentication
			
	#Parse
	try:
		#TODO: log
		print xml
		rspecValue = XmlParser.parseXML(xml)
	except Exception as e:
		#TODO: print to stderr	
		raise e

	#For each type of action call appropiate method in a new thread
	if(rspecValue.query.provisioning != None):
		ServiceThread.startMethodInNewThread(ProvisioningDispatcher.processProvisioning,rspecValue.query.provisioning,notificationCallBackUrl)


'''Main routine, opening the XML-RPC server'''
def main():

	checkArgs()

	#If -b is passed, demonize it 
	if len(sys.argv) == 2 and sys.argv[1] == "-b" :
		forkAndExitFather()

	#XXX: testing	
	#processXmlQuery("https://147.83.206.92:9229",1,sys.argv[1])
	#print "Main ends..." 
	#Engage XMLRPC
	
	XmlRpcServer.createInstanceAndEngage(processXmlQuery)		

	#restore stderr and stdout
	#restoreStdinStderr()
	
	#testing
	#processXmlQuery(sys.argv[1])


#Calling main
if __name__ == "__main__":
    main()
