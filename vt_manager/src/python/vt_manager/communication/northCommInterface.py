from django.http import *
import os, logging
import sys
from vt_manager.models import *
from vt_manager.models.Action import Action as ActionModel
from vt_manager.controller import *
from vt_manager.controller.dispatchers.xmlrpc.DispatcherLauncher import DispatcherLauncher
from vt_manager.communication.utils.XmlHelper import *
from vt_manager.utils.ServiceThread import *
from vt_manager.common.rpc4django import rpcmethod
from vt_manager.common.rpc4django import *
#TODO: Provisional import to make test with VTPlanner. Use SFA API whe stable
from vt_manager.communication.sfa.managers.AggregateManager import AggregateManager

#XXX: Sync Thread for VTPlanner
from vt_manager.utils.SyncThread import *
from vt_manager.utils.ServiceProcess import ServiceProcess
import copy
from threading import Thread

from vt_manager.controller.drivers.VTDriver import VTDriver

from threading import Timer
from vt_manager.controller.actions.ActionController import ActionController
import time
import signal


@rpcmethod(url_name="plugin")
#def send(callBackUrl, expID, xml):
def send(callBackUrl, xml):
	try:
		logging.debug("XML RECEIVED: \n%s" % xml)
		rspec = XmlHelper.parseXmlString(xml)
	except Exception as e:
		logging.error("send() could not parse\n")
		logging.error(e)
		return
	ServiceThread.startMethodInNewThread(DispatcherLauncher.processXmlQuery ,rspec, url = callBackUrl)
	return


@rpcmethod(url_name="plugin")
def send_sync(callBackUrl, xml):
    try:
		logging.debug("XML RECEIVED: \n%s" % xml)
		rspec = XmlHelper.parseXmlString(xml)
    except Exception as e:
		logging.error("sendSync() could not parse \n")
		logging.error(e)
		return
    #SyncThread.startMethodAndJoin(DispatcherLauncher.processXmlQuerySync, rspec, url = callBackUrl)
    #ServiceThread.startMethodInNewThread(DispatcherLauncher.processXmlQuery ,rspec, url = callBackUrl)
    ServiceProcess.startMethodInNewProcess(DispatcherLauncher.processXmlQuerySync ,rspec, url = callBackUrl)
    actionModel = None
    old_handler = signal.signal(signal.SIGALRM, timeout_handler) 
    signal.alarm(10*60) # timeout set on 10 minutes
    while True:
        time.sleep(5)
        try:
	    actionModel = ActionModel.objects.get(uuid=rspec.query.provisioning.action[0].id)
	    if actionModel.getStatus() == "SUCCESS": 
		signal.signal(signal.SIGALRM, old_handler)
		signal.alarm(0)
                return True
	    elif actionModel.getStatus() == "FAILED":
		signal.signal(signal.SIGALRM, old_handler)
		signal.alarm(0)
		raise Exception("The creation of the VM has FAILED")
	except Exception as e:
	    raise Exception("An error has ocurred during the VM creation")
	finally:
	    signal.signal(signal.SIGALRM, old_handler)
	    signal.alarm(0)
    signal.alarm(0)
    return


@rpcmethod(url_name="plugin")    
def ping(challenge):
	return challenge


@rpcmethod(url_name="plugin")
def listResources(remoteHashValue, projectUUID = 'None', sliceUUID ='None'):
	
	v,s = getattr (DispatcherLauncher,"processInformation")(remoteHashValue, projectUUID, sliceUUID)
	return v,s

@rpcmethod(url_name="plugin")
def ListResourcesAndNodes(slice_urn='None'):

	am = AggregateManager()
        options = dict()
  
        if not slice_urn == 'None':
        	options = {"geni_slice_urn":slice_urn}
        
        print '-----------OPTIONS',options
        return AggregateManager().ListResources(options)


from threading import Timer
from vt_manager.controller.actions.ActionController import ActionController
 
def check(rspec):
        actionModel = ActionController.ActionToModel(rspec.query.provisioning.action[0],"provisioning")
        if actionModel.getAction(rspec.query.provisioning.action[0]).status == actionModel.SUCCESS_STATUS or actionModel.getAction(rspec.query.provisioning.action[0]).status == actionModel.FAILED_STATUS:
	        return True	



def timeout_handler(signum, frame):
    raise Exception("TIMEOUT")

