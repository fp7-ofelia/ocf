from django.http import *
from threading import Thread
from vt_manager.common.rpc4django import rpcmethod
from vt_manager.common.rpc4django import *
from vt_manager.communication.utils.XmlHelper import *
from vt_manager.controller import *
from vt_manager.controller.dispatchers.launcher import DispatcherLauncher
from vt_manager.controller.drivers.virt import VTDriver
from vt_manager.models import *
from vt_manager.utils.ServiceThread import *
import copy
import logging

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
	ServiceThread.startMethodInNewThread(DispatcherLauncher.process_query, rspec, url = callBackUrl)
	return

@rpcmethod(url_name="plugin")    
def ping(challenge):
	return challenge

@rpcmethod(url_name="plugin")
def listResources(remoteHashValue, project_uuid = 'None', slice_uuid ='None'):
	v,s = getattr(DispatcherLauncher,"process_information")(remoteHashValue, project_uuid, slice_uuid)
	return v,s
