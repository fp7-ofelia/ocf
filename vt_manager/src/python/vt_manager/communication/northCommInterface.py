from django.http import *
import os, logging
import sys
from vt_manager.models import *
from vt_manager.controller import *
from vt_manager.controller.dispatchers.xmlrpc.DispatcherLauncher import DispatcherLauncher
from vt_manager.communication.utils.XmlHelper import *
from vt_manager.utils.ServiceThread import *
from vt_manager.common.rpc4django import rpcmethod
from vt_manager.common.rpc4django import *
#TODO: Provisional import to make test with VTPlanner. Use SFA API whe stable
from vt_manager.communication.sfa.managers.AggregateManager import AggregateManager

#XXX: Sync Thread for VTPlanner
from vt_manager.utils import SyncThread

import copy
from threading import Thread

from vt_manager.controller.drivers.VTDriver import VTDriver

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
    thread = SyncThread(DispatcherLauncher.processXmlQuerySync, rspec, url = callBackUrl)
    thread.join()
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
